"""viewer/data/tokyo-tilesets.json（コミット済みのビューア用データ）の検査

viewer/app.js は次の項目を前提にしている:
  cities[].code / name / layers
  layers[].id / type / name / url（3D Tiles の tileset.json）/ lod（文字列 "1" "2" など）/ texture
"""
import json
import unittest
from urllib.parse import urlparse

from _helpers import ROOT

DATA = ROOT / "viewer" / "data" / "tokyo-tilesets.json"
DEFAULT_WARD = "13101"  # viewer/app.js の DEFAULT_WARD


class TokyoTilesets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.cities = cls.data["cities"]

    def test_top_level(self):
        for key in ("source", "generated_at", "cities"):
            self.assertIn(key, self.data)
        self.assertGreater(len(self.cities), 0)

    def test_city_fields(self):
        for c in self.cities:
            with self.subTest(city=c.get("code")):
                self.assertRegex(c["code"], r"^\d{5}$")
                self.assertTrue(c["name"])
                self.assertIsInstance(c["layers"], list)
                self.assertGreater(len(c["layers"]), 0)

    def test_city_codes_unique(self):
        codes = [c["code"] for c in self.cities]
        self.assertEqual(len(codes), len(set(codes)), "都市コードが重複しています")

    def test_layer_ids_unique(self):
        ids = [l["id"] for c in self.cities for l in c["layers"]]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        self.assertEqual(dup, [], "レイヤー ID が重複しています")

    def test_layer_fields(self):
        for c in self.cities:
            for l in c["layers"]:
                with self.subTest(layer=l.get("id")):
                    for key in ("id", "type", "name", "url"):
                        self.assertTrue(l.get(key), key)
                    u = urlparse(l["url"])
                    self.assertEqual(u.scheme, "https")
                    self.assertTrue(u.path.endswith("tileset.json"), l["url"])
                    self.assertIsInstance(l.get("texture"), bool)
                    # app.js は l.lod === "2" のように文字列で比較している
                    self.assertTrue(l.get("lod") is None or isinstance(l["lod"], str))
                    self.assertTrue(l["id"].startswith(c["code"]), "レイヤーが別の都市に入っています")

    def test_default_ward_has_buildings(self):
        city = next((c for c in self.cities if c["code"] == DEFAULT_WARD), None)
        self.assertIsNotNone(city, "初期表示の区がデータにありません")
        self.assertTrue(any(l["type"] == "bldg" for l in city["layers"]))

    def test_tokyo_23_wards(self):
        codes = {c["code"] for c in self.cities}
        self.assertTrue(all(code.startswith("131") for code in codes))
        self.assertEqual(len(codes), 23)


if __name__ == "__main__":
    unittest.main()
