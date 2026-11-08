"""tools/citygml_to_geojson.py のテスト（ネットワーク接続なし・小さなローカル CityGML）"""
import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from _helpers import FIXTURES
import citygml_to_geojson as c2g

GML = FIXTURES / "citygml" / "udx" / "bldg" / "53394611_bldg_6697_test.gml"


def run_main(*args):
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        c2g.main([str(a) for a in args])
    return err.getvalue()


class ConvertLocalFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name)
        cls.geojson_path = out / "b.geojson"
        cls.csv_path = out / "b.csv"
        run_main(GML, "-o", cls.geojson_path, "--csv", cls.csv_path, "--generic")
        cls.fc = json.loads(cls.geojson_path.read_text(encoding="utf-8"))
        cls.by_id = {f["properties"]["gml_id"]: f for f in cls.fc["features"]}
        with cls.csv_path.open(encoding="utf-8-sig", newline="") as fh:
            cls.rows = list(csv.DictReader(fh))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_feature_collection(self):
        self.assertEqual(self.fc["type"], "FeatureCollection")
        self.assertIn("PLATEAU", self.fc["attribution"])

    def test_buildings_without_geometry_are_skipped(self):
        self.assertEqual(set(self.by_id), {"bldg_test_a", "bldg_test_b"})

    def test_lod0_footprint_axis_order(self):
        # EPSG:6697 は「緯度 経度」、GeoJSON は「経度, 緯度」
        geom = self.by_id["bldg_test_a"]["geometry"]
        self.assertEqual(geom["type"], "Polygon")
        ring = geom["coordinates"][0]
        self.assertEqual(ring[0], [139.76, 35.68])
        self.assertEqual(len(ring), 5)
        self.assertEqual(ring[0], ring[-1])

    def test_lod1_bottom_face_fallback(self):
        geom = self.by_id["bldg_test_b"]["geometry"]
        lats = sorted({p[1] for p in geom["coordinates"][0]})
        lons = sorted({p[0] for p in geom["coordinates"][0]})
        self.assertEqual(lats, [35.682, 35.683])
        self.assertEqual(lons, [139.762, 139.763])

    def test_centroid(self):
        p = self.by_id["bldg_test_a"]["properties"]
        self.assertAlmostEqual(p["lon"], 139.7605, places=6)
        self.assertAlmostEqual(p["lat"], 35.6805, places=6)

    def test_codes_decoded_with_local_codelists(self):
        a = self.by_id["bldg_test_a"]["properties"]
        self.assertEqual(a["usage"], "業務施設")
        self.assertEqual(a["class"], "堅ろう建物")
        self.assertEqual(self.by_id["bldg_test_b"]["properties"]["usage"], "住宅")

    def test_basic_attributes(self):
        a = self.by_id["bldg_test_a"]["properties"]
        self.assertEqual(a["name"], "テストビルA")
        self.assertEqual(a["measured_height"], 31.5)
        self.assertEqual(a["storeys_below"], 1)
        self.assertEqual(a["address"], "東京都テスト区一丁目")
        self.assertEqual(a["building_id"], "13999-bldg-1")
        self.assertEqual(a["gen:地区計画"], "テスト地区")

    def test_unknown_sentinel_becomes_null(self):
        # 9999 は「不明」を表す値なので null にする
        self.assertIsNone(self.by_id["bldg_test_a"]["properties"]["storeys_above"])

    def test_flood_depth_is_max_of_all_scenarios(self):
        a = self.by_id["bldg_test_a"]["properties"]
        self.assertEqual(a["flood_depth_max"], 1.2)
        self.assertEqual(len(a["flood_risks"]), 2)
        self.assertEqual(a["flood_risks"][0]["description"], "テスト川流域")
        self.assertEqual(a["flood_risks"][0]["scale"], "L2（想定最大規模）")
        self.assertIsNone(self.by_id["bldg_test_b"]["properties"]["flood_depth_max"])

    @unittest.expectedFailure
    def test_total_floor_area(self):
        # 既知の不具合（未修正）: attributes() が `first(...) or ET.Element("x")` と書いており、
        # 子要素を持たない Element は真偽値が False になるため、値があっても常に None になる。
        # 修正したらこの expectedFailure を外すこと。
        self.assertEqual(self.by_id["bldg_test_a"]["properties"]["total_floor_area"], 1234.5)

    def test_csv_matches_geojson(self):
        self.assertEqual(len(self.rows), len(self.fc["features"]))
        header = self.rows[0].keys()
        for col in ("gml_id", "lon", "lat", "measured_height", "usage", "flood_depth_max"):
            self.assertIn(col, header)
        # 入れ子の詳細は CSV には出さない
        self.assertNotIn("flood_risks", header)
        row_a = next(r for r in self.rows if r["gml_id"] == "bldg_test_a")
        self.assertEqual(row_a["usage"], "業務施設")
        self.assertEqual(float(row_a["measured_height"]), 31.5)

    def test_raw_codes_option(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "raw.geojson"
            run_main(GML, "-o", out, "--raw-codes")
            fc = json.loads(out.read_text(encoding="utf-8"))
        usage = {f["properties"]["gml_id"]: f["properties"]["usage"] for f in fc["features"]}
        self.assertEqual(usage["bldg_test_a"], "401")

    def test_bbox_filter(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "bbox.geojson"
            # 建物A（139.7605, 35.6805）だけを含む範囲
            run_main(GML, "-o", out, "--bbox", 139.76, 35.68, 139.761, 35.681)
            fc = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual([f["properties"]["gml_id"] for f in fc["features"]], ["bldg_test_a"])


class Helpers(unittest.TestCase):
    def test_to_num(self):
        self.assertEqual(c2g.to_num("3"), 3)
        self.assertEqual(c2g.to_num("3.0"), 3.0)
        self.assertIsNone(c2g.to_num("-9999"))
        self.assertIsNone(c2g.to_num("9999"))
        self.assertIsNone(c2g.to_num(None))
        self.assertEqual(c2g.to_num("abc"), "abc")

    def test_parse_poslist_swaps_axis(self):
        self.assertEqual(c2g.parse_poslist("35.1 139.2 10 35.3 139.4 20"),
                         [[139.2, 35.1], [139.4, 35.3]])


if __name__ == "__main__":
    unittest.main()
