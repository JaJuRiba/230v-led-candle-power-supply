from pathlib import Path
import json, uuid, itertools
D=Path(__file__).resolve().parent
q=lambda s:json.dumps(str(s),ensure_ascii=False)
n=lambda x:f'{x*1.27:.4f}'.rstrip('0').rstrip('.') if x else '0'
xy=lambda x,y:f'{n(x)} {n(y)}'
seq=itertools.count(); uid=lambda s=None:str(uuid.uuid5(uuid.NAMESPACE_URL,'p1-isolated/'+str(next(seq) if s is None else s)))
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
def place(k,ref,val,x,y,fx,fy,mpn,j=''):
    t,fp,url=libs[k];s=f'(symbol (lib_id "P1:{k}") (at {xy(x,y)} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)})\n'
    for a,b,ax,ay,h in [('Reference',ref,fx,fy,False),('Value',val,fx,fy+1.7,False),('Footprint',fp,x,y,True),('Datasheet',url,x,y,True),('MPN',mpn,x,y,True)]:s+=prop(a,b,ax,ay,1.12 if a=='Value' else 1.27,j,h)+'\n'
    for i,*_ in pins[k]:s+=f'(pin "{i}" (uuid {uid(ref+":"+str(i))}))\n'
    S.append(s+f'(instances (project "p1" (path "/{root}" (reference "{ref}") (unit 1)))))');B.append((ref,val,mpn,fp))
def wire(*pts):
    for a,b in zip(pts,pts[1:]):S.append(f'(wire (pts (xy {xy(*a)}) (xy {xy(*b)})) (stroke (width 0) (type default)) (uuid {uid()}))')
def dot(x,y):S.append(f'(junction (at {xy(x,y)}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')
def label(v,x,y,left=True):S.append(f'(label {q(v)} (at {xy(x,y)} {0 if left else 180}) {eff(1.15,"left bottom" if left else "right bottom")} (uuid {uid()}))')
def note(t,x,y,size=1.4):S.append(f'(text {q(t)} (at {xy(x,y)} 0) {eff(size,"left")} (uuid {uid()}))')

# All drawing coordinates in 1.27 mm units.
fps={'JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal': 'Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal', 'JST_SH_SM10B-SRSS-TB_1x10-1MP_P1.00mm_Horizontal': 'Connector_JST:JST_SH_SM10B-SRSS-TB_1x10-1MP_P1.00mm_Horizontal', 'SOT-23': 'Package_TO_SOT_SMD:SOT-23', 'TO-263-5_TabPin3': 'Package_TO_SOT_SMD:TO-263-5_TabPin3', 'SOT-23-6': 'Package_TO_SOT_SMD:SOT-23-6', 'SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm': 'Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm', 'R_0805_2012Metric': 'Resistor_SMD:R_0805_2012Metric', 'C_0805_2012Metric': 'Capacitor_SMD:C_0805_2012Metric', 'CP_EIA-6032-28_Kemet-C': 'Capacitor_Tantalum_SMD:CP_EIA-6032-28_Kemet-C'}
def ic(k,ref,left,right,foot,url=''):
 ps=[];h=max(len(left),len(right));
 for side,rows in enumerate((left,right)):
  for idx,(num,name,typ) in enumerate(rows):ps.append((num,name,14 if side else -14,(h-1)*2-idx*4,180 if side else 0,typ,3))
 lib(k,ref,box(-11,h*2,11,-h*2),ps,fps[foot],url)
pi='power_in';po='power_out';pa='passive';inp='input';oc='open_collector';s6='SOT-23-6';tj=lambda n:'https://www.ti.com/lit/ds/symlink/'+n+'.pdf'
ic('Input','J',[],[(1,'6V',po),(2,'RET',po),('MP','Mount',pa)],next(n for n in fps if 'SM02' in n))
ic('Harness','J',[(i,'RET' if i%2==0 else 'OUT'+str((i+1)//2),pa) for i in range(1,11)]+[('MP','Mount',pa)],[],next(n for n in fps if 'SM10' in n))
ic('Reverse_P','Q',[(3,'D',pi),(1,'G',inp)],[(2,'S',po)],'SOT-23','https://www.aosmd.com/sites/default/files/res/data_sheets/AO3401A.pdf')
ic('LT1963A','U',[(2,'IN',pi),(1,'SHDN',inp),(3,'GND',pi)],[(4,'OUT',po),(5,'ADJ',inp)],'TO-263-5_TabPin3','https://www.analog.com/media/en/technical-documentation/data-sheets/lt1963a.pdf')
ic('TPS3700','U',[(5,'VDD',pi),(4,'INB-',inp),(3,'INA+',inp),(2,'GND',pi)],[(6,'OUTB',oc),(1,'OUTA',oc)],s6,tj('tps3700'))
ic('TPS2553','U',[(1,'IN',pi),(3,'EN',inp),(2,'GND',pi)],[(6,'OUT',po),(5,'ILIM','output'),(4,'FAULT',oc)],s6,tj('tps2553'))
for k,pre,geo,fp in [('R','R',box(-2,.8,2,-.8),'R_0805_2012Metric'),('Link','JP',line(-2,0,-1,0)+line(-1,0,1,1)+line(1,0,2,0),next(n for n in fps if 'Jumper' in n)),('C','C',line(-.35,-1.5,-.35,1.5)+line(.35,-1.5,.35,1.5),'C_0805_2012Metric'),('Cp','C',line(-.35,-1.5,-.35,1.5)+line(.35,-1.5,.35,1.5)+line(-1.8,1.6,-.8,1.6)+line(-1.3,1.1,-1.3,2.1),'CP_EIA-6032-28_Kemet-C')]:
 l=3.65 if pre=='C' else 2;lib(k,pre,geo,[(1,'~',-4,0,0,pa,l),(2,'~',4,0,180,pa,l)],fps[fp],hidden=True)
def part(k,ref,val,mpn,x,y,nets):
 place(k,ref,val,x,y,x,y-max(r[3] for r in pins[k])-5,mpn)
 for (num,_,dx,dy,ang,*_),net in zip(pins[k],nets,strict=True):
  a,b=x+dx,y-dy
  if net is None:S.append(f'(no_connect (at {xy(a,b)}) (uuid {uid()}))');continue
  end=a+(12 if dx>0 else -12);wire((a,b),(end,b));label(net,end,b,dx>0 and False or dx<0)
G='GND';V='VSEL';I='VIN_SAFE';A='ADJ';E='BR_EN';M='MON';N=None
note('P1   /   FIVE-PAIR SELV DISTRIBUTOR',10,13,2.4);note('6 V DC only   |   250 mA aggregate   |   de-energize and discharge before changing links',10,18)
note('01   POLARITY AND REGULATION',10,24,1.7)
part('Input','J1','6V SELV','SM02B-SRSS-TB(LF)(SN)',23,40,['VIN',G,G]);part('Reverse_P','Q1','AO3401A','AO3401A',78,40,['VIN',G,I]);part('LT1963A','U1','LT1963A-ADJ','LT1963AEQ#TRPBF',140,40,[I,I,G,V,A]);
def cap(r,x,y,net,kind='1u'):
 k,mpn={'1u':('C','C0805C105K3RACTU'),'100n':('C','C0805C104K5RACTU'),'22u / 16V':('Cp','T491C226K016AT')}[kind];part(k,r,kind,mpn,x,y,[net,G])
cap('C1',70,57,I);cap('C2',142,57,V,'22u / 16V')
def res(r,val,mpn,x,y,a,b):part('R',r,val,mpn,x,y,[a,b])
note('02   FEEDBACK   /   JP1 adds lower-leg conductance',10,71,1.7)
for r,v,code,x,a,b in [(1,'1.47k','RT0805BRD071K47L',32,V,A),(2,'1.00k','RT0805BRD071KL',78,A,G),(3,'1.18k','PTFR0805B1K18P9',123,A,'HI_SET')]:res('R'+str(r),v,code,x,83,a,b)
part('Link','JP1','SET HIGH','PCB copper - open',165,83,['HI_SET',G]);note('03   INDEPENDENT RAIL MONITOR   /   JP2 grants high-voltage permission',10,97,1.7)
part('TPS3700','U7','TPS3700DDCR','TPS3700DDCR',41,116,[I,M,G,G,E,N]);cap('C8',94,114,I,'100n');res('R12','10k','RC0805FR-0710KL',142,114,V,E)
for r,v,code,x,a,b in [(9,'71.5k','71K5',32,V,M),(10,'10.0k','10K',78,M,G),(11,'17.4k','17K4',123,M,'HI_OVP')]:res('R'+str(r),v,'RT0805BRD07'+code+'L',x,139,a,b)
part('Link','JP2','OVP HIGH','PCB copper - open',165,139,['HI_OVP',G]);note('Both links open: 3.0 V. Bridge both for 4.5 V. Never change live.',10,155);note('No mains, batteries or downstream backfeed. OVP disables EN; it does not clamp fast pulses.',10,161)
note('04   INDIVIDUAL CURRENT LIMITS',184,24,1.7)
for i in range(5):
 y=39+i*32;j=i+1;part('TPS2553',f'U{i+2}','TPS2553DBVR','TPS2553DBVR',217,y,[V,E,G,f'OUT{j}',f'LIM{j}',N]);cap(f'C{i+3}',198,y+14,V);res(f'R{i+4}','210k','RC0805FR-07210KL',239,y+14,f'LIM{j}',G)
part('Harness','J2','5 x 50 mA','SM10B-SRSS-TB(LF)(SN)',292,88,[n for i in range(1,6) for n in (f'OUT{i}',G)]+[G]);note('Odd: switched positive',267,121);note('Even: common return',267,126)
libtxt=lambda prefix:'\n'.join(f'(symbol "{prefix}{k}" '+v[0] for k,v in libs.items())
(D/'P1.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)\n'+libtxt('')+')\n');(D/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "P1")(type "KiCad")(uri "${KIPRJMOD}/P1.kicad_sym")(options "")(descr "P1 distribution symbols")))\n')
(D/'p1.kicad_sch').write_text(f'(kicad_sch (version 20231120) (generator eeschema) (uuid {root}) (paper "A3") (title_block (title "P1 | SELV candle distribution") (rev "P1") (comment 1 "External isolated DC only - not for mains"))\n(lib_symbols\n'+libtxt('P1:')+')\n'+'\n'.join(S)+'\n(sheet_instances (path "/" (page "1"))))\n')
import csv
with (D/'bom.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','MPN','Footprint']);w.writerows(B)
