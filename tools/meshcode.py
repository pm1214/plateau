#!/usr/bin/env python3
"""地域メッシュコード（JIS X 0410）と緯度経度の変換

PLATEAU の CityGML は 3次メッシュ（約1km四方、8桁）単位でファイルが分かれています。

  python3 tools/meshcode.py 35.681236 139.767125   # → 53394611（東京駅）
  python3 tools/meshcode.py 53394611               # → メッシュの範囲（南西・北東）
"""
from __future__ import annotations

import math
import sys


# 3次メッシュ1つの大きさは 緯度30秒（1/120度）× 経度45秒（1/80度）。
# 浮動小数点の誤差で境界ちょうどの値（例: 139.7625）が 139.76249999… になり、
# 1つ西・南のメッシュになるのを防ぐため、メッシュ単位の個数に直してから
# わずかな余裕（EPS）を足して切り捨てる。EPS はメッシュの 10億分の1（約1マイクロメートル）。
LAT_CELLS_PER_DEG = 120
LON_CELLS_PER_DEG = 80
EPS = 1e-9


def latlon_to_mesh3(lat: float, lon: float) -> str:
    """緯度経度 → 3次メッシュコード（8桁）。境界上の点は北・東側のメッシュに入る。"""
    n = math.floor(lat * LAT_CELLS_PER_DEG + EPS)          # 緯度方向の 30秒の個数
    m = math.floor((lon - 100) * LON_CELLS_PER_DEG + EPS)  # 経度方向（100度から）の 45秒の個数
    p, q, r = n // 80, n % 80 // 10, n % 10   # 1次: 40分=80個、2次: 5分=10個、3次: 30秒
    u, v, w = m // 80, m % 80 // 10, m % 10   # 1次: 1度=80個、2次: 7.5分=10個、3次: 45秒
    return f"{p:02d}{u:02d}{q}{v}{r}{w}"


def mesh3_bounds(code: str) -> tuple[float, float, float, float]:
    """3次メッシュコード → (南, 西, 北, 東)"""
    p, u = int(code[0:2]), int(code[2:4])
    q, v = int(code[4]), int(code[5])
    r, w = int(code[6]), int(code[7])
    # 整数で数えてから1回だけ割ることで、誤差の積み重ねを避ける
    n = p * 80 + q * 10 + r
    m = u * 80 + v * 10 + w
    south, north = n / LAT_CELLS_PER_DEG, (n + 1) / LAT_CELLS_PER_DEG
    west, east = 100 + m / LON_CELLS_PER_DEG, 100 + (m + 1) / LON_CELLS_PER_DEG
    return south, west, north, east


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(latlon_to_mesh3(float(sys.argv[1]), float(sys.argv[2])))
    elif len(sys.argv) == 2:
        s, w, n, e = mesh3_bounds(sys.argv[1])
        print(f"南西 {s:.6f},{w:.6f}  北東 {n:.6f},{e:.6f}")
    else:
        sys.exit(__doc__)
