"""Run after model.py. Read back the manufactured-part exports, not just source solids."""
from itertools import combinations
import numpy as np
import trimesh
from model import *

def clear(a,b):
    volume=a.val().intersect(b.val()).Volume(); assert volume<1e-5, volume
    return volume

base,lid=[cq.importers.importStep(str(OUT/(n+'.step'))) for n in ('base','lid')]
for n,p,h in [('base',base,SEAM),('lid',lid,H-(SEAT+BT+FLOAT))]:
    assert p.val().isValid() and len(p.solids().vals())==1
    m=trimesh.load(OUT/(n+'.stl')); assert m.is_volume and m.body_count==1
    assert np.allclose(m.extents,[L,W,h],atol=.03) and abs(m.bounds[0,2])<.01
    delta=abs(m.volume/p.val().Volume()-1); assert delta<.002
    print(f'{n}: valid single STEP solid; closed oriented STL, {len(m.faces)} triangles; extents {m.extents.round(2)} mm; volume delta {delta:.4%}')
import re, hashlib
r=references(); solids=r['PCBA'].solids().vals()
digest=hashlib.sha256(STEP.read_bytes()).hexdigest()
assert digest=='1145480478ae2fc8be740474f57f734a951be968e47805cecbe825c689199aae'
names=set(re.findall(r"NEXT_ASSEMBLY_USAGE_OCCURRENCE\('[^']*','([A-Z]+[0-9]+)'",STEP.read_text()))
assert names==set(['Q1','J1','J2']+[f'{prefix}{i}' for prefix,count in [('R',12),('C',8),('U',7)] for i in range(1,count+1)])
print(f'Source STEP SHA256 {digest}; {len(names)} fitted references, {len(solids)} solids including substrate; JP1/2 copper only.')
def bounds(s):
    b=s.BoundingBox();return np.array([b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax])
board,=[s for s in solids if abs(s.BoundingBox().xlen-BW)<.001];assert np.allclose(bounds(board),[-19,19,-17,17,5,6.5162])
travel=SEAT+BT+FLOAT-bounds(board)[5]
print('Substrate faces at Z5.0000 and 6.5162; component mounting plane Z6.6000.')
for n,x,od,w in PORTS:
    j,=[b for s in solids if abs((b:=bounds(s))[1]-b[0]-(w-2))<.01 and abs(b[3]-16.17)<.02];assert abs((j[1]+j[0])/2-x)<.001
    print(n,'header bounds',j.round(3))
clear(base,lid)
for a,b in combinations(r.values(),2): clear(a,b)
for v in r.values(): clear(base,v);clear(lid,v)
asm=cq.importers.importStep(str(OUT/'assembly.step'));assert len(asm.solids().vals())==len(solids)+6
# Sweep each component bounding prism: base sees insertion from above;
# lid sees contents below their final position during descent. Include lateral drift.
for obj in solids+[r[n+'_mate'].val() for n,*_ in PORTS]:
    x,X,y,Y,z,Z=bounds(obj); a,b=X-x+2*GAP,Y-y+2*GAP
    clear(base,box(a,b,Z-z+20,(X+x)/2,(Y+y)/2,z))
    clear(lid,box(a,b,Z-z+20+travel,(X+x)/2,(Y+y)/2,z-20))
for n,x,od,w in PORTS:
    # Open-case combined plug extraction and narrow jaw/tool envelope. Rear face
    # starts outside header; jaws enter vertically, then travel along +Y.
    service=box(w+3,18,14,x,25.2,6.6);clear(base,service);clear(r['PCBA'],service)
    for depth,d in [(1.5,od+ENTRY),(6.,od-SQUEEZE)]:
        for shell,up in [(base,-1),(lid,1)]:
            for dr,solid in [(-.025,False),(.025,True)]:
                assert shell.val().isInside((x,FRONT-depth,SEAM+up*(d/2+dr)))==solid
    print(f'{n}: 10 mm extraction / vertical jaw envelope clear; jacket mouth {od+ENTRY:.2f}, grip {od-SQUEEZE:.2f} mm sampled on both halves.')
for x,y in SCREWS:
    bit=cyl(4.8,25,x,y,H-2.2);clear(lid,bit);clear(base,bit)
print('All nominal shell/content pairs clear (<1e-5 mm3); swept PCBA + plug bounding boxes clear base/lid through 20 mm Z and +/-0.55 XY, +0.6338 lift. Four Ø4.8 driver columns clear.')
checks={'locator/side (+0.2 outline, 0.2 inward face)':GAP-.1-.2,'lift (+0.15 board relative to nominal 1.6, 0.30 seat/stop)':FLOAT-.15-.30,'roof over tallest package (+lift and 0.55 stack)':H-ROOF-max(bounds(s)[5] for s in solids)-travel-.55,'service stroke to clamp (10 withdrawal + 0.55 travel + 0.5 error)':46-24.2-10-.55-.5,'screw tip reserve (0.5 combined error)':5.8-(10-(H-2.2-SEAM))-.5,'driver radial reserve (0.15 radial error)':(5.3-4.8)/2-.15}
for k,v in checks.items(): assert v>0;print(f'{k}: {v:.2f} mm residual')
print('PASS: CAD only. Jackets intentionally interfere; retention, real tooling, crimp geometry, fit and temperatures not tested.')
