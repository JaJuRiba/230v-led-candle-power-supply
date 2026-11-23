"""Independent netlist intent, mode corners, and STEP population audit (stdlib)."""
from pathlib import Path
import itertools as it,xml.etree.ElementTree as ET,re
D=Path(__file__).resolve().parent;x=ET.parse(D/'p1.xml');actual={n.get('name').removeprefix('/'):{t.get('ref')+'.'+t.get('pin') for t in n} for n in x.findall('.//nets/net')};expect={}
for n,s in {'VIN':'J1.1 Q1.3','VIN_SAFE':'Q1.2 U1.1 U1.2 U7.5 C1.1 C8.1','ADJ':'U1.5 R1.2 R2.1 R3.1','VSEL':'U1.4 C2.1 R1.1 R9.1 R12.1','MON':'U7.4 R9.2 R10.1 R11.1','HI_OVP':'R11.2 JP2.1','HI_SET':'R3.2 JP1.1','BR_EN':'U7.6 R12.2','GND':'J1.2 J1.MP J2.MP Q1.1 U1.3 U7.2 U7.3 R2.2 JP1.2 JP2.2 R10.2 C1.2 C2.2 C8.2'}.items():expect[n]=set(s.split())
for i in range(1,6):
 u=f'U{i+1}';r=f'R{i+3}';c=f'C{i+2}';expect['OUT'+str(i)]={u+'.6',f'J2.{2*i-1}'};expect['LIM'+str(i)]={u+'.5',r+'.1'};expect['GND'].update([u+'.2',c+'.2',r+'.2',f'J2.{2*i}']);expect['BR_EN'].add(u+'.3');expect['VSEL'].update([u+'.1',c+'.1'])
assert expect=={k:v for k,v in actual.items() if not k.startswith('unconnected-')};nc=[v for k,v in actual.items() if k.startswith('unconnected-')];assert len(nc)==6 and set.union(*nc)=={f'U{i}.4' for i in range(2,7)}|{'U7.1'}
step=(D/'mechanical/p1.step').read_text();refs=re.findall(r"NEXT_ASSEMBLY_USAGE_OCCURRENCE\('[^']+','([A-Z]+[0-9]+)'",step);assert sorted(refs)==sorted(c.get('ref') for c in x.findall('.//comp') if not c.get('ref').startswith('JP'));print('PASS all signal, supply, return and NC sets; STEP:',len(refs),'populated positions.')
# Bind the corner assumptions to the exported components, not just constants.
import csv
components = {c.get('ref'): (c.findtext('value'), c.findtext('fields/field[@name="MPN"]'), c.findtext('footprint')) for c in x.findall('./components/comp')}
with (D/'bom.csv').open(newline='') as f:
 rows = list(csv.DictReader(f))
assert len(rows) == len(components)
assert {r['Reference']: (r['Value'], r['MPN'], r['Footprint']) for r in rows} == components
assert x.findtext('design/source') == 'p1.kicad_sch'
for ref, value, mpn in [('U1','LT1963A-ADJ','LT1963AEQ#TRPBF'), ('R1','1.47k','RT0805BRD071K47L'), ('R2','1.00k','RT0805BRD071KL'), ('R3','1.18k','PTFR0805B1K18P9'), ('R9','71.5k','RT0805BRD0771K5L'), ('R10','10.0k','RT0805BRD0710KL'), ('R11','17.4k','RT0805BRD0717K4L')]:
 assert components[ref][:2] == (value, mpn), (ref, components[ref])
print('PASS BOM/XML; R11 = 17.4k RT0805BRD0717K4L')
def bounds(v,t,b,d,ib,h):
 vals=[v*(1+t*(1/b+h/(d+rc)))+ib*t for v,t,b,d,ib,rc in it.product(v,(t*.998,t*1.002),(b*.998,b*1.002),(d*.998,d*1.002),ib,(0,1))];return min(vals),max(vals)
for h in (0,1):
 reg=bounds((1.174,1.246),1470,1000,1180,(0,10e-6),h);rise=bounds((.396,.404),71500,10000,17400,(-50e-9,50e-9),h);fall=bounds((.387,.400),71500,10000,17400,(-50e-9,50e-9),h);assert reg[1]<min(rise[0],fall[0]);print('HIGH' if h else 'LOW','reg / disable / release (V)',*(tuple(round(n,5) for n in vv) for vv in (reg,rise,fall)))
