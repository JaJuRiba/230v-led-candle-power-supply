"""Build a fresh P1 HOLD candidate. Never save or refill the input board."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from export import CLI, build, require, rows
from inspect_cam import inspect


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def review(board, mapping, out):
    require(board.name == 'p1.kicad_pcb' and not out.exists(), 'Expected P1 and a NEW output directory')
    def run(project, *args):
        subprocess.run([CLI, *args], cwd=project, check=True)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp); saved = root/'saved'; refill = root/'refill'; hand = root/'handoff'
        source_hash = digest(board)
        shutil.copytree(board.parent, saved); shutil.copytree(saved, refill)
        sch = 'p1.kicad_sch'; pcb = board.name
        shutil.copyfile(mapping, root/'procurement.csv')
        run(saved, 'sch','erc','--exit-code-violations','-o','erc.rpt',sch)
        run(saved,'pcb','drc','--schematic-parity','--severity-all','--exit-code-violations','-o','saved-board.rpt',pcb)
        for back in (False,True):
            run(saved,'pcb','export','svg','--mode-single','--page-size-mode','2','--sketch-pads-on-fab-layers',
                *(['--mirror'] if back else []),'-l',('B.Fab,B.Silkscreen' if back else 'F.Fab,F.Silkscreen')+',Edge.Cuts',
                '-o','bottom-viewed-from-below.svg' if back else 'top.svg',pcb)
        require(build(saved/pcb,hand,root/'procurement.csv') == 0, 'Unresolved sourcing')
        for n in (1,2):
            run(refill,'pcb','drc','--refill-zones','--save-board','--schematic-parity','--severity-all','--exit-code-violations','-o',f'refill{n}.rpt',pcb)
            run(refill,'pcb','export','gerbers','-l','F.Cu,In1.Cu,In2.Cu,B.Cu','-o',f'cam{n}',pcb)
        result = inspect(hand/'fabrication.zip',refill/'cam1',refill/'cam2')
        (hand/'cam-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
        require(source_hash == digest(saved/pcb) == digest(board) and digest(saved/sch)==digest(board.with_suffix('.kicad_sch')), 'Input changed')
        for name in ('erc.rpt','saved-board.rpt','top.svg','bottom-viewed-from-below.svg'):
            shutil.copyfile(saved/name,hand/name)
        for i,name in enumerate(('refill.rpt','second-refill.rpt'),1): shutil.copyfile(refill/f'refill{i}.rpt',hand/name)
        shutil.copyfile(root/'procurement.csv',hand/'procurement.csv'); shutil.rmtree(hand/'intermediate')
        # Derive the worksheet from this plot, not last build's placement assumptions.
        import csv, re
        with zipfile.ZipFile(hand/'fabrication.zip') as z:
            plot=z.read('p1-F_Cu.gtl').decode()
        sheet=hand/'placement-review.csv'; records=rows(sheet)
        for row in records:
            m=re.search(r'%TO.P,'+re.escape(row['Ref'])+r',1[,*][^\n]*\n(?:%TO.N,[^\n]*\n)?X(-?\d+)Y(-?\d+)D03',plot)
            require(m,'Missing pin 1 in copper: '+row['Ref'])
            row['Pin 1 / polarity evidence']=f'Gerber pad 1 at ({int(m[1])/1e6:g}, {int(m[2])/1e6:g}) mm; verify vendor preview.'
        with sheet.open('w',newline='') as f:
            writer=csv.DictWriter(f,records[0]); writer.writeheader(); writer.writerows(records)
        (hand/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(hand.iterdir())))
        shutil.copytree(hand,out)
        print('HOLD candidate:',out,'— inspect cam-inspection.json before publication; no order approval.')

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('board','verified_procurement_csv','new_directory'): p.add_argument(arg,type=Path)
    a=p.parse_args(); review(a.board.resolve(),a.verified_procurement_csv.resolve(),a.new_directory.resolve())
