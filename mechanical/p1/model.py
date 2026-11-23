"""P1 standalone LV case. mm; assembled coordinates except print-oriented STLs."""
from pathlib import Path
import cadquery as cq
from cadquery import exporters as ex

OUT = Path(__file__).resolve().parent
# Measure jacket OD at several rotations before using these defaults.
BW, BD, BT = 38., 34., 1.6
IN_OD, OUT_OD = 4., 6.
SQUEEZE, ENTRY = .30, 1.2  # diametral, separate grip and free entry
L, W, CY, FRONT = 60., 78., 16., 55.
T, FLOOR, ROOF, R = 2., 2., 2., 4.
SEAT, SEAM, H = 5., 8.2, 16.
GAP, FLOAT = .55, .55  # lateral gap/side, lift before stops
SCREWS = [(i*(L/2-6), CY+j*(W/2-5)) for i in (-1,1) for j in (-1,1)]

def box(a,b,c,x:float=0,y:float=0,z:float=0):
    return cq.Workplane('XY').box(a,b,c,centered=(True,True,False)).translate((x,y,z))

def rounded(a,b,c,r,z):
    return box(a,b,c,y=CY,z=z).edges('|Z').fillet(r)

def cyl(d,h,x,y,z):
    return cq.Workplane('XY').circle(d/2).extrude(h).translate((x,y,z))

PORTS = [('J1',13.,IN_OD,6.),('J2',-6.,OUT_OD,14.)]
STEP = OUT/'../../hardware/p1/mechanical/p1.step'

def axial(d,x,y1,y2):
    return cq.Workplane('XZ').circle(d/2).extrude(y2-y1).translate((x,y2,SEAM))

def parts():
    base=rounded(L,W,SEAM,R,0).cut(rounded(L-2*T,W-2*T,SEAM,R-T,FLOOR))
    lid=rounded(L,W,H-SEAM,R,SEAM).cut(rounded(L-2*T,W-2*T,H-SEAM,R-T,SEAM-ROOF))
    for x,y in SCREWS:
        base=base.union(cyl(7,SEAM-FLOOR,x,y,FLOOR)).cut(cyl(2.0,6.8,x,y,SEAM-5.8))
        lid=lid.union(cyl(7,H-SEAM,x,y,SEAM)).cut(cyl(2.9,H-SEAM+2,x,y,SEAM-1)).cut(cyl(5.3,3.2,x,y,H-2.2))
    for i in (-1,1):
        for j in (-1,1):
            x,y=i*(BW/2-1),j*(BD/2-1)
            base=base.union(box(6,6,SEAT-FLOOR,x,y,FLOOR))
            # Independent L-shaped locators, open upwards; four small contact zones.
            for a,b,xx,yy in [(1.4,5,i*(BW/2+GAP+.7),y),(1.4,1.4,i*18.8,j*(BD/2+GAP+.7))]:
                base=base.union(box(a,b,BT+1,xx,yy,SEAT))
            stop=SEAT+BT+FLOAT
            lid=lid.union(box(2,2,H-ROOF-stop,x,y,stop))
    for _,x,od,_ in PORTS:
        base=base.union(box(od+5,9,SEAM-FLOOR,x,FRONT-4.5,FLOOR))
        lid=lid.union(box(od+5,9,H-SEAM,x,FRONT-4.5,SEAM))
        for y1,y2,d in [(FRONT-3,FRONT+1,od+ENTRY),(FRONT-9,FRONT-3,od-SQUEEZE)]:
            tool=axial(d,x,y1,y2); base=base.cut(tool); lid=lid.cut(tool)
    return base,lid

def references():
    pcba=cq.importers.importStep(str(STEP)).rotate((0,0,0),(0,0,1),180).translate((19,-17,SEAT))
    r={'PCBA':pcba}
    for n,x,od,w in PORTS:
        r[n+'_mate']=box(w,8,4,x,20.2,6.6)
        r[n+'_fanout']=box(w,21.8,od,x,35.1,SEAM-od/2)
    return r

def assemble(base,lid,ref):
    a=cq.Assembly(name='P1_integrated'); a.add(base,name='base',color=cq.Color(.16,.26,.32)); a.add(lid,name='lid',color=cq.Color(.70,.77,.79));
    for n,v in ref.items(): a.add(v,name=n,color=cq.Color(.20,.55,.33) if n=='PCBA' else cq.Color(.79,.60,.28))
    return a

def view(name,shapes,direction):
    c=cq.Compound.makeCompound([s.val() for s in shapes]); ex.export(c,str(OUT/(name+'.svg')),opt={'width':640,'height':420,'showAxes':False,'showHidden':False,'projectionDir':direction,'strokeWidth':.55,'strokeColor':(30,60,75)})

if __name__=='__main__':
    base,lid=parts(); refs=references()
    for n,p,printpart in [('base',base,base),('lid',lid,lid.rotate((0,0,0),(1,0,0),180).translate((0,0,H)))]:
        ex.export(p,str(OUT/(n+'.step'))); ex.export(printpart,str(OUT/(n+'.stl')),tolerance=.025,angularTolerance=.12)
    assemble(base,lid,refs).save(str(OUT/'assembly.step'))
    view('closed',[base,lid],(1,1,.8)); view('open',[base,*refs.values()],(1,1,1.4)); view('exploded',[base,refs['PCBA'].translate((0,0,23)),lid.translate((0,0,41))],(1,-2,.85))
