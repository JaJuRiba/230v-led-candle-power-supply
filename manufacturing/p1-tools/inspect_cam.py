"""Independent reader for the linear, dark-only KiCad P1 CAM subset (not general RS-274X)."""
import json
import re
import sys
import zipfile
from collections import Counter
from decimal import Decimal
from pathlib import Path
from export import require

LAYERS = ('p1-F_Cu.gtl', 'p1-In1_Cu.g1', 'p1-In2_Cu.g2', 'p1-B_Cu.gbl')


def parse(text):
    require(all(s in text for s in ('%FSLAX46Y46*%', '%MOMM*%', '%LPD*%')), 'Unknown units/format')
    definitions = dict(re.findall(r'%ADD(\d+)([^*]+)\*%', text))
    macros = re.findall(r'%AM.*?\*%', text, re.S)
    body = text.split('G04 APERTURE END LIST*', 1)[1]
    flashes, strokes, regions = Counter(), Counter(), []
    contour = pos = aperture = None
    for line in body.strip().splitlines():
        if line.startswith(('%TO.', '%TD', '%TA.', 'G04')) or line in ('G01*', 'M02*'):
            continue
        if line == 'G36*':
            contour = []
        elif line == 'G37*':
            require(contour and contour[0] == contour[-1], 'Unclosed region')
            regions.append(tuple(contour)); contour = None
        elif m := re.fullmatch(r'D(\d+)\*', line):
            aperture = definitions[m[1]]
        else:
            m = re.fullmatch(r'X(-?\d+)Y(-?\d+)D0([123])\*', line)
            require(m, 'Unsupported plot operation: ' + line)
            point = int(m[1]), int(m[2])
            if contour is not None:
                require(m[3] == ('1' if contour else '2'), 'Unexpected region command')
                contour.append(point)
            elif m[3] == '3':
                flashes[aperture, point] += 1
            elif m[3] == '1':
                strokes[aperture, tuple(sorted((pos, point)))] += 1
            pos = point
    require(contour is None, 'Unterminated region')
    return flashes, strokes, Counter(regions), macros


def area(regions):
    # Twice the signed area in integer square nanometres; keyed holes cancel.
    return sum(n * abs(sum(x*b-y*a for (x,y),(a,b) in zip(p,p[1:]))) for p,n in regions.items())


def compare(a, b):
    f,s,p,m = parse(a); g,t,q,n = parse(b)
    return dict(flashes_equal=f==g, strokes_equal=s==t, macros_equal=m==n,
                region_paths_equal=p==q, changed_saved_regions=sum((p-q).values()),
                region_area_delta_mm2=(area(q)-area(p))/2e12)


def inspect(archive, first, second):
    with zipfile.ZipFile(archive) as z:
        def text(name): return z.read(name).decode()
        layers = {name:parse(text(name)) for name in LAYERS}
        comparisons = {}
        for name in LAYERS:
            a = (first/name).read_text(); b = (second/name).read_text()
            comparisons[name] = dict(saved_to_refill=compare(text(name), a), refill_to_next=compare(a,b))
        def points(name): return {p for _,p in parse(text(name))[0]}
        mask, paste = points('p1-F_Mask.gts'), points('p1-F_Paste.gtp')
        cu = points(LAYERS[0])
        links = {(x,-94200000) for x in (127350000,128650000,132350000,133650000)}
        tab = (117375000,-87000000)
        windows = {(x,y) for x in (114950000,119800000) for y in (-89775000,-84225000)}
        require(mask <= cu and paste == (mask-links-{tab})|windows and links|{tab} <= mask, 'Mask/paste/jumper registration')
        require(not any(parse(text('p1-B_Mask.gbs'))[:3]), 'Unexpected back mask openings')
        edge = parse(text('p1-Edge_Cuts.gm1')); corners = [(100,-80),(138,-80),(138,-114),(100,-114)]
        expected = Counter(tuple(sorted(((a*1000000,b*1000000),(x*1000000,y*1000000)))) for (a,b),(x,y) in zip(corners,corners[1:]+corners[:1]))
        require(not edge[0] and not edge[2] and Counter({s:n for (_,s),n in edge[1].items()}) == expected, 'Outline differs')
        def holes(name):
            return {(int(Decimal(x)*1000000),int(Decimal(y)*1000000)) for x,y in re.findall(r'^X([-\d.]+)Y([-\d.]+)$',text(name),re.M)}
        drill = holes('p1-PTH.drl')
        require(not holes('p1-NPTH.drl') and 'T1C0.300' in text('p1-PTH.drl') and len(drill)==78, 'Drill inventory')
        for name,(flashes,_,_,_) in layers.items():
            require({p for (ap,p) in flashes if ap=='C,0.650000'}==drill, 'Via registration '+name)
        headers = {(x*100000,-108700000) for x in [1055,1065]+list(range(1205,1296,10))}
        mounts = {p for p in paste if p[1]==-112575000}
        require(headers <= paste and len(mounts)==4 and (108225000,-83600000) in paste, 'Connector/U1 alignment')
        return dict(copper=comparisons, outline_mm=corners, via_drills=len(drill), npth=0,
                    mask_openings=len(mask), paste_openings=len(paste), jumper_lands_without_paste=len(links),
                    header_signal_lands=len(headers), header_mount_lands=len(mounts))

if __name__ == '__main__':
    print(json.dumps(inspect(*map(Path,sys.argv[1:])),indent=2))
