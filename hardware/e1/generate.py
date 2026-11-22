"""Rebuild E1 from this directory (overwrites native sources; not needed to edit them)."""
from pathlib import Path
import json, uuid, itertools
D=Path(__file__).resolve().parent
q=lambda s:json.dumps(str(s),ensure_ascii=False)
n=lambda x:f'{x*1.27:.4f}'.rstrip('0').rstrip('.') if x else '0'
xy=lambda x,y:f'{n(x)} {n(y)}'
seq=itertools.count(); uid=lambda s=None:str(uuid.uuid5(uuid.NAMESPACE_URL,'e1-bench/'+str(next(seq) if s is None else s)))
root=uid('root'); S=[]; libs={}; pins={}; B=[]
def eff(size=1.27,j='',hide=False):return f'(effects (font (size {size} {size})) '+(f'(justify {j})' if j else '')+(' (hide yes)' if hide else '')+')'
def prop(k,v,x,y,sz=1.27,j='',hide=False):return f'(property {q(k)} {q(v)} (at {xy(x,y)} 0) {eff(sz,j,hide)})'
st='(stroke (width 0.254) (type default))';fill='(fill (type none))'
def box(x,y,a,b):return f'(rectangle (start {xy(x,y)}) (end {xy(a,b)}) {st} {fill})'
def line(x,y,a,b):return f'(polyline (pts (xy {xy(x,y)}) (xy {xy(a,b)})) {st} {fill})'
def lib(k,pref,geom,ps,fp,url='',hidden=False):
    pins[k]=ps
    t=(f'(pin_names (offset 0.508)'+(' (hide yes)' if hidden else '')+') '+('(pin_numbers (hide yes))' if hidden else '')+' (in_bom yes) (on_board yes) ')
    for a,b in [('Reference',pref),('Value',k),('Footprint',fp),('Datasheet',url)]:t+=prop(a,b,0,0,hide=a not in ('Reference','Value'))+'\n'
    t+=f'(symbol "{k}_0_1" {geom})\n(symbol "{k}_1_1" '
    for i,name,x,y,ang,typ,length in ps:t+=f'(pin {typ} line (at {xy(x,y)} {ang}) (length {n(length)}) (name {q(name)} {eff(1.15)}) (number "{i}" {eff(1.0)}))\n'
    libs[k]=(t+'))',fp,url)
ST='https://www.st.com/resource/en/datasheet/ld1117.pdf';TI='https://www.ti.com/lit/ds/symlink/tps2553.pdf'
fpj='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'
lib('LD1117V','U',box(-8,4,8,-4),[(3,'IN',-11,0,0,'power_in',3),(2,'OUT',11,0,180,'power_out',3),(1,'ADJ',0,-7,90,'input',3)],'Package_TO_SOT_THT:TO-220-3_Vertical',ST)
lib('TPS2553DBVR','U',box(-9,6,9,-6),[(1,'IN',-12,3,0,'power_in',3),(3,'EN',-12,0,0,'input',3),(2,'GND',-12,-3,0,'power_in',3),(6,'OUT',12,3,180,'power_out',3),(4,'~{FAULT}',12,0,180,'open_collector',3),(5,'ILIM',12,-3,180,'output',3)],'Package_TO_SOT_SMD:SOT-23-6',TI)
for k,a,geom,fp in [('R','R',box(-2,0.8,2,-0.8),'Resistor_SMD:R_0805_2012Metric'),('Shunt','JP',box(-2,1.2,2,-1.2)+line(-1.3,0,-.7,0)+line(.7,0,1.3,0),fpj)]:lib(k,a,geom,[(1,'~',-4,0,0,'passive',2),(2,'~',4,0,180,'passive',2)],fp,hidden=k=='R')
for k,pol in [('C',False),('Cpol',True)]:lib(k,'C',line(-1.7,.4,1.7,.4)+line(-1.7,-.4,1.7,-.4)+(line(-2,1.7,-1,1.7)+line(-1.5,1.2,-1.5,2.2) if pol else ''),[(1,'~',0,3,270,'passive',2.6),(2,'~',0,-3,90,'passive',2.6)],'Capacitor_Tantalum_SMD:CP_EIA-6032-28_Kemet-C' if pol else 'Capacitor_SMD:C_0805_2012Metric',hidden=True)
for k,d in [('BenchInput',1),('BranchOutput',-1)]:lib(k,'J',box(-4,3.5,4,-3.5),[(1,'+',d*6,2,180 if d==1 else 0,'power_out' if d==1 else 'passive',2),(2,'RET',d*6,-2,180 if d==1 else 0,'power_out' if d==1 else 'passive',2)],fpj)
def place(k,ref,val,x,y,fx,fy,mpn,j=''):
    t,fp,url=libs[k];s=f'(symbol (lib_id "E1:{k}") (at {xy(x,y)} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)})\n'
    for a,b,ax,ay,h in [('Reference',ref,fx,fy,False),('Value',val,fx,fy+1.7,False),('Footprint',fp,x,y,True),('Datasheet',url,x,y,True),('MPN',mpn,x,y,True)]:s+=prop(a,b,ax,ay,1.12 if a=='Value' else 1.27,j,h)+'\n'
    for i,*_ in pins[k]:s+=f'(pin "{i}" (uuid {uid(ref+":"+str(i))}))\n'
    S.append(s+f'(instances (project "e1" (path "/{root}" (reference "{ref}") (unit 1)))))');B.append((ref,val,mpn,fp))
def wire(*pts):
    for a,b in zip(pts,pts[1:]):S.append(f'(wire (pts (xy {xy(*a)}) (xy {xy(*b)})) (stroke (width 0) (type default)) (uuid {uid()}))')
def dot(x,y):S.append(f'(junction (at {xy(x,y)}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')
def label(v,x,y,left=True):S.append(f'(label {q(v)} (at {xy(x,y)} {0 if left else 180}) {eff(1.15,"left bottom" if left else "right bottom")} (uuid {uid()}))')
def note(t,x,y,size=1.4):S.append(f'(text {q(t)} (at {xy(x,y)} 0) {eff(size,"left")} (uuid {uid()}))')
def cap(r,x,y,bulk=False):place('Cpol' if bulk else 'C',r,'22 µF / 16 V' if bulk else '1 µF / 25 V',x,y,x+3,y-1,'T491C226K016AT' if bulk else 'C0805C105K3RACTU','left')
header='Samtec TSW-102-07-G-S'; shunt='Samtec SNT-100-BK-G'
note('E1   /   ISOLATED DC BENCH SUPPLY',16,14,2.4);note('One shared voltage setting for all five outputs. No mains connection.',16,19)
note('01   INPUT AND SHARED REGULATOR',16,29,1.8)
place('BenchInput','J1','LAB INPUT',22,44,22,37,header);place('LD1117V','U1','LD1117V',79,42,79,34,'LD1117V');wire((28,42),(48,42),(68,42));label('VIN',48,42);dot(48,42);cap('C1',48,52);wire((48,42),(48,49));wire((48,55),(48,60));label('GND',48,60);wire((28,46),(32,46),(32,60));label('GND',32,60)
wire((90,42),(111,42),(135,42));dot(111,42);label('VSEL',135,42,False);cap('C2',111,52,True);wire((111,42),(111,49));wire((111,55),(111,60));label('GND',111,60);wire((79,49),(79,58));label('ADJ',79,58)
note('02   FEEDBACK AND POWER-OFF SELECTOR',16,75,1.8)
wire((20,94),(35,94),(54,94));label('VSEL',20,94);dot(35,94);place('R','R1','120 Ω',58,94,58,89,'Vishay TNPW0805120RBETA');wire((62,94),(86,94),(100,94));dot(86,94);label('ADJ',86,94);place('R','R2','167 Ω',104,94,104,89,'Vishay TNPW0805167RBETY');wire((108,94),(125,94));label('GND',125,94,False)
wire((35,94),(35,106),(46,106));place('R','R3','140 Ω',50,106,50,101,'Vishay TNPW0805140RBEEN');wire((54,106),(56,106),(68,106));label('SEL_LINK',56,106);place('Shunt','JP1','4.5 V SELECT',72,106,72,101,header);wire((76,106),(86,106),(86,94))
for i,t in enumerate(['JP1 open: 3.0 V. Fit shunt for 4.5 V; never change live.','J1: 6.05–6.15 V at the pins; isolated lab supply, limit 0.40 A.','J1 and J2–J6: pin 1 positive, pin 2 common return.','50 mA continuous per branch; 250 mA total. Not LED current sources.','FAULT pins intentionally unused. No output overvoltage shutdown.','Verify the empty outputs before connecting any battery-free load.']):note(t,16,121+i*4.5)
note('03   CURRENT-LIMITED OUTPUTS',163,15,1.8)
for b in range(1,6):
    y=32+(b-1)*35; u=b+1; rr=b+3
    place('TPS2553DBVR',f'U{u}','TPS2553DBVR',216,y,216,y-10,'TPS2553DBVR');cap(f'C{b+2}',180,y+4)
    wire((164,y-3),(180,y-3),(198,y-3),(204,y-3));dot(180,y-3);dot(198,y-3);wire((198,y-3),(198,y),(204,y));wire((180,y-3),(180,y+1));label('VSEL',164,y-3);wire((180,y+7),(180,y+13));label('GND',180,y+13);wire((204,y+3),(198,y+3),(198,y+13));label('GND',198,y+13)
    place('BranchOutput',f'J{u}',f'OUT {b}',292,y-1,292,y-9,header);wire((228,y-3),(252,y-3),(286,y-3));label(f'OUT{b}',252,y-3);wire((286,y+1),(280,y+1),(280,y+13));label('GND',280,y+13);S.append(f'(no_connect (at {xy(228,y)}) (uuid {uid()}))');wire((228,y+3),(232,y+3),(232,y+10),(248,y+10));label(f'LIM{b}',232,y+10);place('R',f'R{rr}','210 kΩ / 1%',252,y+10,252,y+4.5,'Yageo RC0805FR-07210KL');wire((256,y+10),(268,y+10));label('GND',268,y+10,False)
libtxt=lambda prefix:'\n'.join(f'(symbol "{prefix}{k}" '+v[0] for k,v in libs.items())
(D/'E1.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)\n'+libtxt('')+')\n');(D/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "E1")(type "KiCad")(uri "${KIPRJMOD}/E1.kicad_sym")(options "")(descr "E1 bench prototype symbols")))\n')
(D/'e1.kicad_sch').write_text(f'(kicad_sch (version 20231120) (generator eeschema) (uuid {root}) (paper "A3") (title_block (title "E1 | Five-output bench supply") (rev "E1") (comment 1 "External isolated DC only - not for mains"))\n(lib_symbols\n'+libtxt('E1:')+')\n'+'\n'.join(S)+'\n(sheet_instances (path "/" (page "1"))))\n')
import csv
with (D/'bom.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','Part or specification','Footprint']);w.writerows(B);w.writerow(['JP1 accessory','Removable shunt',shunt,''])
