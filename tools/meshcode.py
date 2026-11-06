#!/usr/bin/env python3
"""地域メッシュコード（JIS X 0410）と緯度経度の変換

PLATEAU の CityGML は 3次メッシュ（約1km四方、8桁）単位でファイルが分かれています。

  python3 tools/meshcode.py 35.681236 139.767125   # → 53394611（東京駅）
  python3 tools/meshcode.py 53394611               # → メッシュの範囲（南西・北東）
"""
from __future__ import annotations

import sys


def latlon_to_mesh3(lat: float, lon: float) -> str:
    """緯度経度 → 3次メッシュコード（8桁）"""
    p, a = divmod(lat * 60, 40)          # 1次: 緯度40分
    q, b = divmod(a, 5)                  # 2次: 緯度5分
    r, c = divmod(b * 60, 30)            # 3次: 緯度30秒
    u, f = divmod(lon - 100, 1)          # 1次: 経度1度
    v, g = divmod(f * 60, 7.5)           # 2次: 経度7.5分
    w, _ = divmod(g * 60, 45)            # 3次: 経度45秒
    return f"{int(p):02d}{int(u):02d}{int(q)}{int(v)}{int(r)}{int(w)}"


def mesh3_bounds(code: str) -> tuple[float, float, float, float]:
    """3次メッシュコード → (南, 西, 北, 東)"""
    p, u = int(code[0:2]), int(code[2:4])
    q, v = int(code[4]), int(code[5])
    r, w = int(code[6]), int(code[7])
    south = p / 1.5 + q * 5 / 60 + r * 30 / 3600
    west = u + 100 + v * 7.5 / 60 + w * 45 / 3600
    return south, west, south + 30 / 3600, west + 45 / 3600


if __name__ == "__main__":
    if len(sys.argv) == 3:
        print(latlon_to_mesh3(float(sys.argv[1]), float(sys.argv[2])))
    elif len(sys.argv) == 2:
        s, w, n, e = mesh3_bounds(sys.argv[1])
        print(f"南西 {s:.6f},{w:.6f}  北東 {n:.6f},{e:.6f}")
    else:
        sys.exit(__doc__)
