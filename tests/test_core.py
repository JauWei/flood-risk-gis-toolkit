import csv
import tempfile
import unittest
from pathlib import Path
from floodrisk.core import normalize, analyze, read_cells, save_csv, save_geojson


class RiskTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize([1, 3, 5]), [0, .5, 1])
        self.assertEqual(normalize([2, 2]), [0, 0])

    def test_invalid(self):
        with self.assertRaises(ValueError):
            normalize([float("nan")])

    def test_risk_bounds(self):
        cells = read_cells(Path(__file__).resolve().parents[1] / "data/sample_cells.csv")
        result = analyze(cells)
        self.assertEqual(len(result), len(cells))
        self.assertTrue(all(0 <= r["risk_index"] <= 1 for r in result))
        with tempfile.TemporaryDirectory() as tmp:
            save_csv(result, Path(tmp) / "risk.csv")
            save_geojson(result, Path(tmp) / "risk.geojson")
            self.assertTrue((Path(tmp) / "risk.csv").exists())
            self.assertTrue((Path(tmp) / "risk.geojson").exists())

    def test_bad_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.csv"
            p.write_text("cell_id,x,y,elevation_m,slope_deg,rainfall_mm,impervious_pct,population\na,0,0,1,2,10,101,5\n")
            with self.assertRaisesRegex(ValueError, "Invalid row"):
                read_cells(p)


if __name__ == "__main__":
    unittest.main()
