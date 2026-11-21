"""Independent delivery checks against M0 nominal dimensions, not builder inputs."""
from math import hypot, prod
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh

p = Path(__file__).resolve().parent
assert __debug__, 'Do not disable assertions'
svg = ET.parse(p/'m0-section.svg').getroot()
w, h = (float(svg.get(key).removesuffix('mm')) for key in ('width', 'height'))
assert all(svg.get(key).endswith('mm') for key in ('width', 'height'))
assert list(map(float, svg.get('viewBox').split())) == [0, 0, w, h]

def rect(name):
    node = svg.find(f".//{{*}}rect[@id='{name}']")
    return [float(node.get(k)) for k in ('x', 'y', 'width', 'height')]

sx, sy, sw, sh = rect('screen')
assert [sw, sh] == [54, 64]
cursor = sy + sh
for name, size in [('irm03', (37, 24, 15)), ('shelly', (34, 29, 16))]:
    mesh = trimesh.load_mesh(p/f'm0-{name}.stl', process=True)
    assert mesh.body_count == 1 and mesh.is_volume and mesh.euler_number == 2
    assert mesh.nondegenerate_faces().all()
    assert np.allclose(mesh.extents, size, atol=0.001, rtol=0)
    assert abs(mesh.bounds[0, 2]) < 0.001 and abs(mesh.volume-prod(size)) < 0.001
    cursor -= size[2]
    assert np.allclose(rect(name), [sx+(sw-size[0])/2, cursor, size[0], size[2]], atol=0.001, rtol=0)
    assert hypot(*size[:2]) < sw
    print(f'{name}: {mesh.extents} mm; {mesh.volume:g} mm³; one closed, consistently wound solid; diagonal {hypot(*size[:2]):.2f} mm')
assert cursor-sy == 33
print('PASS: SVG physical scale and centred section match STL dimensions; 31 mm stack, 33 mm unallocated in assumed section.')
