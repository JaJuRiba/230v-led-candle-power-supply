"""Normalize only the local source filename in a KiCad XML export."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

path = Path(__file__).with_name('p1.xml')
text = path.read_text()
source = ET.fromstring(text).findtext('design/source')
assert source and source.replace(chr(92), '/').split('/')[-1] == 'p1.kicad_sch'
text, count = re.subn(r'(<design>\s*<source>)[^<]+(</source>)',
                      r'\g<1>p1.kicad_sch\2', text, count=1)
assert count == 1
path.write_text(text)
