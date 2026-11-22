"""E1 only: compare drawn wiring and optionally a KiCad XML export against pin intent."""
from pathlib import Path
from collections import defaultdict
import re,json,sys,xml.etree.ElementTree as ET
if not __debug__: raise SystemExit("Run checks without -O")
D=Path(__file__).resolve().parent
intent={'VIN':'J1.1 U1.3 C1.1','VSEL':'U1.2 C2.1 R1.1 R3.1','ADJ':'U1.1 R1.2 R2.1 JP1.2','SEL_LINK':'R3.2 JP1.1','GND':'J1.2 C1.2 C2.2 R2.2'}
nc=set()
for i in range(1,6):
    u=i+1;c=i+2;r=i+3
    intent['VSEL']+=f' U{u}.1 U{u}.3 C{c}.1';intent['GND']+=f' U{u}.2 J{u}.2 C{c}.2 R{r}.2';intent[f'OUT{i}']=f'U{u}.6 J{u}.1';intent[f'LIM{i}']=f'U{u}.5 R{r}.1';nc.add(f'U{u}.4')
intent={k:set(v.split()) for k,v in intent.items()}
def parse(s):
    stack=[[]]
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()"]+',s):
        if t=='(':x=[];stack[-1].append(x);stack.append(x)
        elif t==')':stack.pop()
        else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert len(stack)==1 and len(stack[0])==1;return stack[0][0]
def many(x,k):return [a for a in x if isinstance(a,list) and a[0]==k]
def one(x,k):a,=many(x,k);return a
def pt(x):return tuple(round(float(a)*10000) for a in x[1:3])
s=parse((D/'e1.kicad_sch').read_text());libs={l[1]:l for l in many(one(s,'lib_symbols'),'symbol')};parent={}
def root(a):
    if a not in parent:parent[a]=a
    while parent[a]!=a:a=parent[a]
    return a
def join(a,b):parent[root(a)]=root(b)
P={};wpts=set();labels={};ncs={pt(one(z,'at')) for z in many(s,'no_connect')}
for z in many(s,'wire'):
    a,b=map(pt,many(one(z,'pts'),'xy'));join(a,b);wpts.update((a,b))
for l in many(s,'label'):
    a=pt(one(l,'at'));assert a in wpts;join(a,l[1]);labels[l[1]]=a
for u in many(s,'symbol'):
    lib=libs[one(u,'lib_id')[1]];ref=next(p[2] for p in many(u,'property') if p[1]=='Reference');at=one(u,'at');assert at[3]=='0' and not many(u,'mirror');x,y=pt(at)
    for unit in many(lib,'symbol'):
        for pin in many(unit,'pin'):
            dx,dy=pt(one(pin,'at'));a=x+dx,y-dy;key=f'{ref}.{one(pin,"number")[1]}';assert key not in P;P[key]=a
actual={name:{k for k,a in P.items() if root(a)==root(p)} for name,p in labels.items()};assert actual==intent,(actual,intent);assert {k for k,a in P.items() if a in ncs}==nc and not ncs&wpts;assert set(P)==set.union(nc,*intent.values());print(f'Drawn pin map PASS: {len(many(s,"symbol"))} parts, {len(P)} pins, {len(intent)} named nets, {len(nc)} marked NC.')
if len(sys.argv)>1:
    nets={}; seen_nc=set(); names=set()
    for n in ET.parse(sys.argv[1]).findall('.//nets/net'):
        pins={p.attrib['ref']+'.'+p.attrib['pin'] for p in n.findall('node')}
        name=n.attrib['name'].lstrip('/')
        assert name not in names; names.add(name)
        if pins<=nc:
            assert len(pins)==1 and pins.isdisjoint(seen_nc); seen_nc.update(pins); continue
        nets[name]=pins
    assert seen_nc==nc
    assert nets==intent,(nets,intent);print('KiCad XML named nets PASS.')
if '--' not in sys.argv:
    for k,v in intent.items():print(k,':',' '.join(sorted(v)))
