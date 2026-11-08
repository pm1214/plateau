"""tools/plateau_catalog.py のテスト（API には接続しない）"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _helpers import FIXTURES
import plateau_catalog as pc

SAMPLE = json.loads((FIXTURES / "catalog_sample.json").read_text(encoding="utf-8"))


class FilterDatasets(unittest.TestCase):
    items = SAMPLE["latest_datasets"]

    def ids(self, **kw):
        return [x["id"] for x in pc.filter_datasets(self.items, **kw)]

    def test_pref(self):
        got = self.ids(pref="13")
        self.assertNotIn("14100_bldg_lod1", got)
        self.assertEqual(len(got), 5)

    def test_city_by_code_or_name(self):
        self.assertEqual(self.ids(city="13102"), ["13102_bldg_lod1"])
        self.assertEqual(self.ids(city="中央区"), ["13102_bldg_lod1"])

    def test_city_prefix_selects_23_wards(self):
        got = self.ids(city_prefix="131")
        self.assertIn("13101_bldg_lod1", got)
        self.assertNotIn("13201_bldg_lod1", got)

    def test_type_and_format(self):
        self.assertEqual(self.ids(city="13101", types=["tran"]), ["13101_tran_mvt"])
        self.assertNotIn("13101_tran_mvt", self.ids(city="13101", fmt="3d tiles"))


class ViewerJson(unittest.TestCase):
    def test_generate_from_sample(self):
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(pc, "load_catalog", return_value=SAMPLE), \
                contextlib.redirect_stderr(io.StringIO()):
            out = Path(d) / "v.json"
            pc.main(["viewer-json", "--pref", "13", "--city-prefix", "131", "--out", str(out)])
            data = json.loads(out.read_text(encoding="utf-8"))
        codes = [c["code"] for c in data["cities"]]
        self.assertEqual(codes, ["13101", "13102"])  # 23区のみ・コード順
        chiyoda = data["cities"][0]
        # MVT は 3D Tiles ビューアに載せない
        self.assertEqual([l["id"] for l in chiyoda["layers"]],
                         ["13101_bldg_lod1", "13101_bldg_lod2_no_texture"])
        # 名前の末尾の「（千代田区）」は落とす
        self.assertEqual(chiyoda["layers"][0]["name"], "建築物モデル")


class CityGmlIndexCondition(unittest.TestCase):
    def requested_url(self, condition):
        with mock.patch.object(pc, "http_get", return_value=b'{"cities": []}') as m:
            pc.fetch_citygml_index(condition)
        return m.call_args[0][0]

    def test_mesh_code_gets_prefix(self):
        self.assertTrue(self.requested_url("53394611").endswith("/citygml/m:53394611"))

    def test_city_code_is_passed_through(self):
        self.assertTrue(self.requested_url("13101").endswith("/citygml/13101"))


if __name__ == "__main__":
    unittest.main()
