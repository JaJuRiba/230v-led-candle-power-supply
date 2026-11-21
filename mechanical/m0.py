"""Build M0 in this file's directory. All design parameters are in mm."""
from pathlib import Path
from math import hypot
import cadquery as cq

OUT = Path(__file__).resolve().parent
# X (long side), Y, Z. Solid envelopes, no shrink/clearance offset.
PARTS = {'shelly': (34, 29, 16), 'irm03': (37, 24, 15)}
WIDTH, DEPTH = 54, 64  # screening assumptions only


def build():
    blocks = []
    for name, (x, y, z) in PARTS.items():
        block = cq.Workplane('XY').box(x, y, z, centered=(True, True, False))
        assert len(block.solids().vals()) == 1 and block.val().isValid()
        cq.exporters.export(block, str(OUT / f'm0-{name}.stl'))
        blocks.append(block)
    # Centred X-Z section at Y=0, with the IRM against the imaginary back.
    cx, top = WIDTH/2 + 8, 17
    page_w, page_h = max(WIDTH+16, 82), top+DEPTH+15
    bottom = top + DEPTH
    rects = []
    cursor = bottom
    for name, block, color in zip(reversed(PARTS), reversed(blocks), ['#dbebf8', '#fae3bd']):
        bb = block.val().BoundingBox()
        cursor -= bb.zlen
        rects.append(f'<rect id="{name}" x="{cx-bb.xlen/2}" y="{cursor}" width="{bb.xlen}" height="{bb.zlen}" fill="{color}" stroke="#263743" stroke-width="0.25"/>')
        rects.append(f'<text x="{cx}" y="{cursor+bb.zlen/2+1}" text-anchor="middle">{name.upper()} · {bb.xlen:g} × {bb.zlen:g}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{page_w}mm" height="{page_h}mm" viewBox="0 0 {page_w} {page_h}" font-family="sans-serif" font-size="2.8" fill="#213240">
<title>M0 | Centre section of loose stack, X–Z (mm)</title>
<text x="5" y="6" font-size="4">M0 / Centre section · X–Z</text>
<text x="5" y="12">Dashed: assumed {WIDTH} wide × {DEPTH} deep (mm)</text>
<rect id="screen" x="8" y="{top}" width="{WIDTH}" height="{DEPTH}" fill="none" stroke="#657684" stroke-width="0.3" stroke-dasharray="1 1"/>
<text x="10" y="{top+5}">Opening plane</text>
<text x="10" y="{(top+cursor)/2+3}">{cursor-top:g} nominal / unallocated</text>
{''.join(rects)}
<text x="5" y="{bottom+5}">Back plane · no cover, bosses or wiring modeled</text>
<path d="M5 {bottom+10}h10" stroke="#263743" stroke-width="0.6"/><text x="17" y="{bottom+11}">10 mm at 100% · not a box drawing</text>
</svg>'''
    (OUT / 'm0-section.svg').write_text(svg+'\n', encoding='utf-8')


if __name__ == '__main__':
    build()
