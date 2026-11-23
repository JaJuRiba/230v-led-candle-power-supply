"""Rebuild from KiCad XML, including placement, plane escapes and grid routes. Run KiCad DRC with refill/save afterwards."""
from pathlib import Path
import re,uuid,json,math,heapq,itertools,os,xml.etree.ElementTree as ET
os.chdir(Path(__file__).resolve().parent)
q=json.dumps;uid=lambda:f'(uuid "{uuid.uuid4()}")';xml=ET.parse('p1.xml');net={};pin={};S=[];a=S.append
P=dict(J1=(6,30.7),J2=(25,30.7),U1=(14,7),Q1=(5.5,15.2),C1=(3.35,5),C2=(11.4,15.4),R1=(17,16.1),R2=(20,13.8),R3=(23.4,14.2),JP1=(28,14.2),JP2=(33,14.2),U7=(29,6),C8=(33.5,6),R9=(24.2,8.8),R10=(28.8,10),R11=(33.5,10),R12=(24,4))
for i in range(5):
 x=5+i*7;P.update({f'U{i+2}':(x,22),f'C{i+3}':(x,18.8),f'R{i+4}':(x,25.4)})
a('(kicad_pcb (version 20260206)(generator pcbnew)(general(thickness 1.6))(paper "A4")(layers (0 "F.Cu" signal)(4 "In1.Cu" power)(6 "In2.Cu" power)(2 "B.Cu" signal)(13 "F.Paste" user)(5 "F.SilkS" user)(1 "F.Mask" user)(7 "B.Mask" user)(25 "Edge.Cuts" user)(47 "F.CrtYd" user)(49 "F.Fab" user))(setup(pad_to_mask_clearance 0))')
S[0]=S[0].replace('(setup(', '(setup '+Path('stackup.sexpr').read_text()+'(')
for n in xml.findall('.//nets/net'):
 name=n.get('name');net[name]=n.get('code');a(f'(net {net[name]} {q(name)})');
 for t in n:pin[t.get('ref'),t.get('pin')]=name,t.attrib
pads=[];geom=[];X=100;Y=80
for c in xml.findall('.//comp'):
 r=c.get('ref');lib=c.findtext('footprint');l,f=lib.split(':');s=Path(f'footprints/{l}.pretty/{f}.kicad_mod').read_text();x,y=P[r];s=s.replace(q(f),q(lib),1);s=re.sub(r'\n\t\((?:version|generator|generator_version) [^\n]+','',s);s=re.sub(r'\(uuid "[^"]*"\)',lambda m:uid(),s);s=s.replace('(layer "F.Cu")',f'(layer "F.Cu") {uid()} (at {X+x} {Y+y}) (path "/{c.findtext("tstamps")}") (sheetname "/") (sheetfile "p1.kicad_sch")',1);s=s.replace('"REF**"',q(r),1).replace('(property "Value" '+q(f),'(property "Value" '+q(c.findtext('value')),1)
 # Move silk refs into a consistent side location, on fab for crowded passives.
 s=re.sub(r'(\(property "Reference" [^\n]+\s+\(at )[^)]+(\)\s+\(layer )"F.SilkS"',lambda m:m[1]+'0 0 0'+m[2]+'"F.Fab"',s,count=1)
 for field in ['MPN','Datasheet']:
  val=c.findtext(f'fields/field[@name="{field}"]');
  if val:
   if f'(property "{field}"' in s:s=re.sub(r'\(property "'+field+'" "[^"]*"',f'(property "{field}" {q(val)}',s,count=1)
   else:s=s.replace('(attr ',f'(property "{field}" {q(val)} (at 0 0)(layer "F.Fab")(hide yes)(effects(font(size 1 1))))\n\t(attr ',1)
 if r.startswith("JP"):s=s.replace(" exclude_from_bom", "")
 def pad(m):
  num=m[1];dx,dy=map(float,m[2].split()[:2]);w,h=map(float,m[3].split());
  if not num:return m[0]
  n,att=pin[r,num];pt=(x+dx,y+dy);pads.append((r,num,n,pt,w,h));geom.append((0,n,*pt,w/2,h/2,'pad'));add=f'(net {net[n]} {q(n)})(pintype {q(att["pintype"])})';return m[0]+add+(f'(pinfunction {q(att["pinfunction"])})' if 'pinfunction' in att else '')
 s=re.sub(r'\(pad "([^"]*)" [^\n]+\s+\(at ([^)]+)\)\s+\(size ([^)]+)\)',pad,s);a(s)
L=['F.Cu','B.Cu'];sc=4;W=153;H=137;Z=W*H
idx=lambda x,y:round(x*sc)+round(y*sc)*W
pt=lambda i:((i%W)/sc,((i%Z)//W)/sc)
def seg(n,l,u,v,w):
 if u!=v:a(f'(segment(start {X+u[0]:.5f} {Y+u[1]:.5f})(end {X+v[0]:.5f} {Y+v[1]:.5f})(width {w})(layer "{L[l]}")(net {net[n]}){uid()})')
def via(n,u):
 x,y=u;a(f'(via(at {X+x} {Y+y})(size 0.65)(drill 0.3)(layers "F.Cu" "B.Cu")(net {net[n]}){uid()})');geom.extend((l,n,x,y,.325,.325,'via') for l in range(2))
def masks(n,w):
 b=bytearray(Z*2);v=bytearray(Z)
 def block(arr,l,x,y,rx,ry):
  x1=max(0,math.ceil((x-rx)*sc));x2=min(W-1,math.floor((x+rx)*sc));hh=b'\1'*(x2-x1+1)
  for j in range(max(0,math.ceil((y-ry)*sc)),min(H-1,math.floor((y+ry)*sc))+1):
   off=l*Z+j*W+x1;arr[off:off+len(hh)]=hh
 for l,t,x,y,rx,ry,kind in geom:
  if n!=t:block(b,l,x,y,rx+w/2+.24,ry+w/2+.24)
  if t!=n or kind in ('pad','via'):block(v,0,x,y,rx+.325+.23,ry+.325+.23)
 return b,v
def route(n,u,t,w):
 b,v=masks(n,w);start=idx(*u);target=idx(*t) if t else None;seq=itertools.count();pq=[(0,0,next(seq),start)];prev={start:-1};ds={start:0}
 while pq:
  _,d,_,i=heapq.heappop(pq)
  if d!=ds[i]:continue
  if i==target or (target is None and not v[i%Z]):break
  for di,cost in [(1,10),(-1,10),(W,10),(-W,10),(1+W,14),(-1-W,14),(1-W,14),(W-1,14)]+([(Z if i<Z else -Z,100)] if t and not v[i%Z] else []):
   j=i+di;x,y=pt(j);nd=d+cost
   if x<1.25 or x>36.75 or y<.75 or y>33.25 or b[j] or nd>=ds.get(j,10**9):continue
   if abs(di) in (W-1,W+1) and (b[i+(1 if (di%W)==1 else -1)] or b[i+(W if di>0 else -W)]):continue
   h=0 if not t else max(abs(x-t[0]),abs(y-t[1]))*40;ds[j]=nd;prev[j]=i;heapq.heappush(pq,(nd+h,nd,next(seq),j))
 else:raise ValueError(('no route',n,u,t))
 path=[]
 while i!=-1:path.append(i);i=prev[i]
 path.reverse();last=u;dire=None;pr=path[0];layer=0
 # exact-center lead-in stays inside pad. GND/VSEL routes terminate in an off-pad via.
 seg(n,0,u,pt(pr),w);last=pt(pr)
 for j in path[1:]:
  di=j-pr
  if di!=dire:seg(n,layer,last,pt(pr),w);last=pt(pr);dire=di
  if abs(di)==Z:via(n,pt(pr));layer=j//Z
  geom.append((layer,n,*pt(j),w/2,w/2,'track'));pr=j
 seg(n,layer,last,pt(pr),w)
 if t:seg(n,0,pt(pr),t,w)
 else:via(n,pt(pr))
# Stitch beyond (not through) solderable tab copper. Additional ground spreading on both outer layers.
for x in (13,15,17,19,21):
 for y in (.85,13):
  if y==13 and x<20:continue
  via('/GND',(x,y))
for n in ['/GND','/VSEL']:
 for r,num,nn,u,w,h in pads:
  if n==nn:route(n,u,None,.35 if n=='/VSEL' else .26)
for n in ['/ADJ','/MON','/VIN_SAFE','/VIN']+[k for k in net if k.startswith('/') and k not in ('/ADJ','/MON','/VIN_SAFE','/VIN','/VSEL','/GND')]:
 todo=[p[3] for p in pads if p[2]==n];done=[todo.pop(0)]
 while todo:
  _,s,t=min((math.dist(s,t),s,t) for s in done for t in todo);route(n,s,t,.45 if n in ('/VIN','/VIN_SAFE') else .23);done.append(t);todo.remove(t)
a(f'(gr_rect(start {X} {Y})(end {X+38} {Y+34})(stroke(width .05)(type solid))(fill no)(layer "Edge.Cuts"){uid()})')
for n,l in [('/GND','In1.Cu'),('/VSEL','In2.Cu'),('/GND','B.Cu'),('/GND','F.Cu')]:
 a(f'(zone(net {net[n]})(net_name {q(n)})(layer {q(l)}){uid()}(hatch edge .5)(connect_pads yes(clearance .25))(min_thickness .2)(fill yes(thermal_gap .3)(thermal_bridge_width .3))(polygon(pts(xy {X} {Y})(xy {X+38} {Y})(xy {X+38} {Y+34})(xy {X} {Y+34}))))')
for txt,x,y in [('P1  SELV',14,29),('6V',10.8,32),('1+',16.6,30),('SET',28,16.5),('OVP',33,16.5)]:a(f'(gr_text {q(txt)}(at {X+x} {Y+y})(layer "F.SilkS"){uid()}(effects(font(size .85 .85)(thickness .14))))')
a(')');Path('p1.kicad_pcb').write_text('\n'.join(S));print(len(pads),'lands;',len(S),'board elements')
