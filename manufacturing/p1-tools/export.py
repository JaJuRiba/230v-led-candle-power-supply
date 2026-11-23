"""KiCad 10.0.8 two/four-layer, default-variant manufacturing review bundle."""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

CLI = os.environ.get('KICAD_CLI') or 'kicad-cli'
LAYERS = {'F.Cu': 'gtl', 'B.Cu': 'gbl', 'In1.Cu': 'g1', 'In2.Cu': 'g2', 'F.Mask': 'gts', 'B.Mask': 'gbs',
          'F.Paste': 'gtp', 'B.Paste': 'gbp', 'F.SilkS': 'gto', 'B.SilkS': 'gbo', 'Edge.Cuts': 'gm1'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def children(node, key):
    return [i for i in node if isinstance(i, list) and i[0] == key]


def board_data(path):
    # Tokenize quoted strings before parentheses; only inspect direct children.
    stack = [[]]
    for tok in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^()\s"]+', path.read_text()):
        if tok == '(':
            node = []
            stack[-1].append(node)
            stack.append(node)
        elif tok == ')':
            stack.pop()
        else:
            stack[-1].append(tok.strip('"'))
    require(len(stack) == 1, 'Malformed board')
    root, = stack[0]
    layers = {i[1] for i in children(root, 'layers')[0][1:]}
    require({i for i in layers if i.endswith('.Cu')} in ({'F.Cu', 'B.Cu'}, {'F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu'}), 'Unsupported copper stack')
    require({'F.Mask', 'B.Mask', 'Edge.Cuts'} <= layers, 'Missing required masks or outline')
    fps = {}
    for fp in children(root, 'footprint'):
        ref, = [i[2] for i in children(fp, 'property') if i[1] == 'Reference']
        require(ref not in fps, f'Duplicate board ref {ref}')
        xy = children(fp, 'at')[0]
        fps[ref] = (children(fp, 'layer')[0][1], float(xy[1]), float(xy[2]))
    return layers, fps


def placement(row, board):
    side, x, y = board
    sx, sy, rot = (float(row[k]) for k in ('PosX', 'PosY', 'Rot'))
    require(abs(sx-x) <= 1e-5 and abs(sy+y) <= 1e-5 and math.isfinite(rot),
            f"Origin, units or angle mismatch at {row['Ref']}")
    expected = {'F.Cu': 'top', 'B.Cu': 'bottom'}[side]
    require(row['Side'] == expected, f"Side mismatch at {row['Ref']}")
    return [row['Ref'], row['PosX'], row['PosY'], format(rot % 360, '.10g'), expected.title()]


def rows(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write_csv(path, header, data):
    with path.open('x', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


def indexed(path):
    data = rows(path)
    result = {i['Ref']: i for i in data}
    require(result and len(result) == len(data) and all(re.fullmatch(r'[A-Za-z]+[0-9]+', r) for r in result),
            f'Empty, duplicate or non-individual designators in {path}')
    return result


def zip_check(path, expected):
    with zipfile.ZipFile(path) as z:
        require(sorted(z.namelist()) == sorted(expected) and z.testzip() is None, 'ZIP inventory/CRC mismatch')
        for name in expected:
            content = z.read(name).strip()
            tokens = (b'M48', b'METRIC', b'absolute / metric / decimal', b'M30') if name.endswith('.drl') else (
                b'%MOMM*%', b'%TF.SameCoordinates,Original*%', b'M02*')
            require(all(t in content for t in tokens), f'Invalid CAM header/trailer: {name}')


def check_r11(path):
    matches = [row for row in rows(path) if 'R11' in row['Designator'].split(',')]
    require(len(matches) == 1 and tuple(matches[0][k] for k in
            ('Designator', 'Quantity', 'Comment', 'MPN', 'LCSC Part #')) ==
            ('R11', '1', '17.4k', 'RT0805BRD0717K4L', 'C133380'),
            'R11: delivered BOM must specify the reviewed 17.4k part')


def build(board, out, sourcing):
    sch = board.with_suffix('.kicad_sch')
    require(board.suffix == '.kicad_pcb' and sch.is_file(), 'Supply matching board and root schematic')
    require(re.fullmatch('[A-Za-z0-9_-]+', board.stem), 'Use an ASCII project stem')
    layers, fps = board_data(board)
    out.mkdir(parents=True, exist_ok=False)
    raw = out / 'intermediate'
    raw.mkdir()
    cam = raw / 'cam'
    cam.mkdir()

    def run(*args):
        return subprocess.run([CLI, *map(str, args)], check=True, text=True, stdout=subprocess.PIPE).stdout

    require(run('version').strip() == '10.0.8', 'Wrong KiCad version')
    run('pcb', 'export', 'gerbers', '-l', ','.join(k.replace('SilkS', 'Silkscreen') for k in LAYERS if k in layers), '-o', cam, board)
    run('pcb', 'export', 'drill', '--excellon-separate-th', '--drill-origin', 'absolute', '-o', cam, board)
    expected = [f'{board.stem}-{k.replace(".", "_").replace("SilkS", "Silkscreen")}.{ext}' for k, ext in LAYERS.items() if k in layers]
    expected += [f'{board.stem}-{kind}.drl' for kind in ('PTH', 'NPTH')]
    require({p.name for p in cam.iterdir() if p.suffix != '.gbrjob'} == set(expected), 'Unexpected/missing CAM files')
    archive = out / 'fabrication.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(expected):
            z.write(cam/name, name)
    zip_check(archive, expected)
    fields = 'Reference,Value,Footprint,MPN,LCSC Part #,LCSC,QUANTITY'
    run('sch', 'export', 'bom', '--exclude-dnp', '--fields', fields, '--labels', 'Ref,Val,FP,MPN,Code,Alias,Qty', '-o', raw/'parts.csv', sch)
    run('pcb', 'export', 'pos', '--exclude-dnp', '--format', 'csv', '--units', 'mm', '--side', 'both', '-o', raw/'positions.csv', board)
    parts, positions = indexed(raw/'parts.csv'), indexed(raw/'positions.csv')
    # Copper-only solder links have no purchasable body. Do not infer this
    # from the JP prefix (a removable shunt header can be a real placement).
    copper_links = [r for r, p in parts.items() if p['MPN'] == 'PCB copper - open'
                    and p['FP'].startswith('Jumper:SolderJumper-') and r in fps]
    for ref in copper_links:
        del parts[ref]
        positions.pop(ref, None)
    require(parts and parts.keys() == positions.keys(), f'BOM/CPL mismatch: {sorted(parts.keys() ^ positions.keys())}')
    verified = {}
    for row in rows(sourcing):
        refs = row['Designator'].split(',')
        require(len(refs) == int(row['Quantity/PCB']), 'Bad sourcing quantity')
        for ref in refs:
            require(ref not in verified, 'Duplicate sourcing reference: ' + ref)
            verified[ref] = (row['Exact MPN'], row['JLC/LCSC ID'])
    require(parts.keys() == verified.keys(), 'Verified sourcing reference set differs')
    groups = defaultdict(list)
    places, issues = [], []
    for ref, part in parts.items():
        pos = positions[ref]
        require(part['Qty'] == '1' and part['FP'].split(':')[-1] == pos['Package'] and part['Val'] == pos['Val'], f'Qty/footprint/value mismatch: {ref}')
        places.append(placement(pos, fps[ref]))
        mpn = part['MPN'].strip()
        codes = {part[k].strip() for k in ('Code', 'Alias') if part[k].strip()}
        require(len(codes) <= 1, f'Conflicting LCSC fields: {ref}')
        source_mpn, code = verified[ref]
        require(source_mpn == mpn and (not codes or codes == {code}), 'Sourcing mismatch: ' + ref)
        if not mpn or re.search(r'\b(TBD|TBC|TODO|unknown|generic|DNI|DNP|unresolved|N/A)\b|\?', mpn, re.I) or mpn in ('-', '~'):
            issues.append(f'{ref}: unresolved MPN')
        if not re.fullmatch(r'C[1-9]\d*', code):
            issues.append(f'{ref}: unresolved LCSC')
        groups[part['Val'], part['FP'], mpn, code].append(ref)
    write_csv(out/'bom.csv', ['Comment', 'Footprint', 'MPN', 'LCSC Part #', 'Designator', 'Quantity'],
              [(*key, ','.join(refs), len(refs)) for key, refs in groups.items()])
    check_r11(out/'bom.csv')
    write_csv(out/'cpl.csv', ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer'], places)
    # Preserve a per-reference record for comparison with the actual JLC part.
    write_csv(out/'placement-review.csv',
              ['Ref', 'MPN', 'Side', 'KiCad X mm', 'KiCad Y mm', 'KiCad rotation deg',
               'Approved X', 'Approved Y', 'Approved rotation', 'Pin 1 / polarity evidence', 'Reviewer', 'Status'],
              [[r, parts[r]['MPN'], side, x, y, angle, '', '', '', '', '', 'NOT REVIEWED']
               for r, x, y, angle, side in places])
    exploded = []
    for row in rows(out/'bom.csv'):
        refs = row['Designator'].split(',')
        require(len(refs) == int(row['Quantity']), 'Bad grouped quantity')
        exploded.extend(refs)
    require(sorted(exploded) == sorted(parts) == sorted(r['Designator'] for r in rows(out/'cpl.csv')), 'Written reference mismatch')
    report = dict(status='HOLD: not approved for PCBA', unresolved=issues, board=board.name,
                  sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (board, sch, sourcing, archive, out/'bom.csv', out/'cpl.csv')},
                  zip_members=expected, disabled_layers=sorted(LAYERS.keys()-layers),
                  omitted_board_refs=sorted(fps.keys()-parts.keys()), placements=len(parts),
                  top=sum(p[-1]=='Top' for p in places), bottom=sum(p[-1]=='Bottom' for p in places), bom_groups=len(groups))
    (out/'review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'{out}/review.json: {len(parts)} placements; {len(issues)} unresolved sourcing fields. Manual review required.')
    return 2 if issues else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', type=Path)
    parser.add_argument('new_output_directory', type=Path)
    parser.add_argument('sourcing', type=Path)
    args = parser.parse_args()
    sys.exit(build(args.board.resolve(), args.new_output_directory.resolve(), args.sourcing.resolve()))
