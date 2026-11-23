import tempfile
from pathlib import Path
import unittest
import export
from export import placement


class PlacementTest(unittest.TestCase):
    def test_delivered_r11_not_just_source(self):
        import csv
        candidate = Path(__file__).resolve().parents[1] / 'p1-candidate' / 'bom.csv'
        with tempfile.TemporaryDirectory() as tmp:
            for field, wrong in [('Comment', '18.2k'), ('MPN', 'RT0805BRD0718K2L'),
                                 ('Designator', 'R111'), ('LCSC Part #', 'C123')]:
                records = export.rows(candidate)
                next(row for row in records if row['Designator'] == 'R11')[field] = wrong
                path = Path(tmp) / field
                with path.open('w', newline='') as f:
                    w = csv.DictWriter(f, records[0]); w.writeheader(); w.writerows(records)
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'R11'):
                    export.check_r11(path)

    def test_bottom_board_origin_not_mirrored(self):
        row = dict(Ref='D1', PosX='12', PosY='-8', Rot='-90', Side='bottom')
        self.assertEqual(placement(row, ('B.Cu', 12, 8)), ['D1', '12', '-8', '270', 'Bottom'])
        for key, value in [('PosX', '-12'), ('PosY', '8'), ('Side', 'top'), ('Rot', 'nan')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                placement(dict(row, **{key: value}), ('B.Cu', 12, 8))


if __name__ == '__main__':
    unittest.main()
