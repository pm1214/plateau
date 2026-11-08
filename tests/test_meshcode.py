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
        # （境界ちょうどの値も含む）
        for lat in [24.3, 26.2, 31.6, 33.59, 35.68, 38.27, 43.06, 45.4, 24.3013, 35.6813]:
            for lon in [123.1, 127.68, 130.4, 135.5, 139.76, 141.35, 145.5, 123.1017, 139.7617]:
                code = latlon_to_mesh3(lat, lon)
                s, w, n, e = mesh3_bounds(code)
                self.assertTrue(s <= lat < n and w <= lon < e, (lat, lon, code))
                c_lat, c_lon = (s + n) / 2, (w + e) / 2
                self.assertEqual(latlon_to_mesh3(c_lat, c_lon), code)

    def test_decimal_boundary_values(self):
        # 10進数で書いた境界ちょうどの値が、2進数の誤差で1つ西・南のメッシュにならないこと
        # （以前の不具合: 35.675, 139.7625 が 53394610 になっていた）
        self.assertEqual(latlon_to_mesh3(35.675, 139.7625), "53394611")
        self.assertEqual(latlon_to_mesh3(35.65001, 139.1), "53393088")
        self.assertEqual(latlon_to_mesh3(26.2, 130.4), "39302342")

    def test_every_southwest_corner_maps_to_its_mesh(self):
        # 日本の範囲の 3次メッシュの南西角（mesh3_bounds の値）を間引いて走査し、
        # その点が同じメッシュに判定されることを確かめる
        for n in range(20 * 120, 46 * 120, 7):
            for m in range(22 * 80, 54 * 80, 11):
                p, q, r = n // 80, n % 80 // 10, n % 10
                u, v, w = m // 80, m % 80 // 10, m % 10
                code = f"{p:02d}{u:02d}{q}{v}{r}{w}"
                s, w_, _, _ = mesh3_bounds(code)
                self.assertEqual(latlon_to_mesh3(s, w_), code)

    def test_bounds_are_exact_decimal_values(self):
        # 範囲の端が 26.200000000000003 のようにずれないこと
        s, w, n, e = mesh3_bounds("39302342")
        self.assertEqual((s, w), (26.2, 130.4))

if __name__ == "__main__":
    unittest.main()
