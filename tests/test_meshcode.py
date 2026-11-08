"""tools/meshcode.py のテスト（地域メッシュコード ⇔ 緯度経度）"""
import unittest

from _helpers import ROOT  # noqa: F401  (tools/ を import パスに追加する)
from meshcode import latlon_to_mesh3, mesh3_bounds

# 3次メッシュ1つの大きさ（度）
DLAT = 30 / 3600
DLON = 45 / 3600


class KnownValues(unittest.TestCase):
    def test_tokyo_station(self):
        # 東京駅（丸の内駅舎付近）は 53394611
        self.assertEqual(latlon_to_mesh3(35.681236, 139.767125), "53394611")

    def test_bounds_of_tokyo_station_mesh(self):
        s, w, n, e = mesh3_bounds("53394611")
        self.assertAlmostEqual(s, 35.675, places=9)
        self.assertAlmostEqual(w, 139.7625, places=9)
        self.assertAlmostEqual(n, 35.675 + DLAT, places=9)
        self.assertAlmostEqual(e, 139.7625 + DLON, places=9)

    def test_code_format(self):
        code = latlon_to_mesh3(35.0, 139.0)
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isdigit())


class Boundaries(unittest.TestCase):
    """メッシュの境界上の点は、南西側の辺を含むメッシュ（北・東側）に属する。"""

    def test_just_inside_and_outside(self):
        eps = 1e-7
        self.assertEqual(latlon_to_mesh3(35.675 + eps, 139.7625 + eps), "53394611")
        self.assertEqual(latlon_to_mesh3(35.675 - eps, 139.7625 + eps), "53394601")
        self.assertEqual(latlon_to_mesh3(35.675 + eps, 139.7625 - eps), "53394610")

    def test_first_level_boundary(self):
        # 1次メッシュの境界（緯度 40分ごと、経度 1度ごと）をまたぐと上4桁が変わる
        self.assertEqual(latlon_to_mesh3(35.3333334, 139.0000001)[:4], "5339")
        self.assertEqual(latlon_to_mesh3(35.3333332, 138.9999999)[:4], "5238")

    def test_center_roundtrip(self):
        # 日本の範囲を粗く走査し、メッシュ中心 → コード → 範囲 が元に戻ることを確かめる
        # 境界ちょうどの値は下の既知の不具合に当たるため、境界から少しずらした点を使う
        for lat in [24.3013, 26.2013, 31.6013, 33.5913, 35.6813, 38.2713, 43.0613, 45.4013]:
            for lon in [123.1017, 127.6817, 130.4017, 135.5017, 139.7617, 141.3517, 145.5017]:
                code = latlon_to_mesh3(lat, lon)
                s, w, n, e = mesh3_bounds(code)
                self.assertTrue(s <= lat < n and w <= lon < e, (lat, lon, code))
                c_lat, c_lon = (s + n) / 2, (w + e) / 2
                self.assertEqual(latlon_to_mesh3(c_lat, c_lon), code)

    @unittest.expectedFailure
    def test_decimal_boundary_float_error(self):
        # 既知の不具合（未修正）: 10進数で書いた境界値が 2進数の浮動小数点で
        # わずかに小さくなり、1つ西（または南）のメッシュに判定される。
        # 例: 53394611 の南西角 (35.675, 139.7625) が 53394610 になる。
        #     経度 139.1 は …8 列の西端なので 53393088 が正しいが 53393087 になる。
        # 修正したらこの expectedFailure を外すこと。
        self.assertEqual(latlon_to_mesh3(35.675, 139.7625), "53394611")
        self.assertEqual(latlon_to_mesh3(35.65001, 139.1), "53393088")


if __name__ == "__main__":
    unittest.main()
