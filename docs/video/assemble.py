"""撮った画面とスライドをつないで、台本どおりの3分の動画（音声なし）を作る。
15fps のフレームを書き出し、ffmpeg で MP4（1920x1080, 30fps）にする。"""
import os, subprocess, sys
from PIL import Image

V = sys.argv[1]
SH, SL, FR = f"{V}/shots", f"{V}/slides", f"{V}/frames"
OUT = sys.argv[2]
FPS = 15
W, H = 1920, 1080
os.makedirs(FR, exist_ok=True)
for f in os.listdir(FR):
    os.remove(os.path.join(FR, f))

cache = {}
def img(path):
    if path not in cache:
        cache[path] = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
    return cache[path]

def zoom(im, z, cx=0.5, cy=0.5):
    """z 倍に拡大して中心 (cx, cy) あたりを切り出す（ゆっくりズーム用）"""
    if z <= 1.0001:
        return im
    w, h = int(W / z), int(H / z)
    x = int((W - w) * cx); y = int((H - h) * cy)
    return im.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)

frames = []  # (関数 t->Image) を1フレームずつ
def still(path, sec, z0=1.0, z1=1.0, cx=0.5, cy=0.5):
    n = int(sec * FPS)
    for i in range(n):
        z = z0 + (z1 - z0) * i / max(1, n - 1)
        frames.append(lambda z=z: zoom(img(path), z, cx, cy))

def fade(a, b, sec):
    """a から b へクロスフェード"""
    n = int(sec * FPS)
    for i in range(n):
        frames.append(lambda i=i: Image.blend(img(a), img(b), (i + 1) / n))

def reveal(before, after, sec, left_px):
    """数えた点が上から1行ずつ増えていく様子（パネルより右の景色の部分）。最後にパネルも結果に替わる"""
    n = int(sec * FPS)
    rows = 25
    for i in range(n):
        k = int(rows * (i + 1) / n)  # 何行目まで出すか
        def f(k=k):
            im = img(before).copy()
            ybot = int(H * k / rows)
            if ybot > 0:
                im.paste(img(after).crop((left_px, 0, W, ybot)), (left_px, 0))
            return im
        frames.append(f)

S = lambda n: f"{SH}/{n}.png"
P = lambda n: f"{SL}/{n}.png"

# ---- 台本（docs/presentation3.md）の時間割
still(S("A_overview"), 9.4, 1.0, 1.08, 0.5, 0.45)                 # 0:00–0:10 上から見た街
fade(S("A_overview"), P("s1-01"), 0.6)
still(P("s1-01"), 9.4)                                               # 0:10–0:20 表紙
fade(P("s1-01"), S("B_years00"), 0.6)
ys = ["B_years00", "B_years10", "B_years20", "B_years30", "B_years40"]  # 0:20–0:40 年数スライダー
for a, b in zip(ys, ys[1:]):
    still(S(a), 3.2)
    fade(S(a), S(b), 0.8)
still(S(ys[-1]), 2.8)
fade(S(ys[-1]), S("C_window"), 0.6)
still(S("C_window"), 9.4)                                            # 0:40–0:50 窓の景色
reveal(S("C_window"), S("D_counted"), 14.0, int(350 * 1.5))          # 0:50–1:04 点が増える
still(S("D_counted"), 15.4, 1.0, 1.06, 0.0, 0.0)                     # 1:04–1:20 結果（パネル側へ寄る）
fade(S("D_counted"), S("E_rank"), 0.6)
still(S("E_rank"), 19.4, 1.0, 1.05, 0.0, 0.6)                        # 1:20–1:40 ベスト5の1位が光る
fade(S("E_rank"), S("F_future"), 1.0)
still(S("F_future"), 29.0, 1.0, 1.06, 0.0, 0.0)                      # 1:40–2:10 20年後の景色
fade(S("F_future"), S("G_sunset_panel"), 0.6)
still(S("G_sunset_panel"), 5.4)                                      # 2:10–2:30 夕日
gs = ["G_sun930", "G_sun950", "G_sun970", "G_sun990", "G_sun1005"]
fade(S("G_sunset_panel"), S(gs[0]), 0.6)
for a, b in zip(gs, gs[1:]):
    still(S(a), 2.6)
    fade(S(a), S(b), 0.6)
still(S(gs[-1]), 0.6)
fade(S(gs[-1]), P("s15-15"), 0.6)
still(P("s15-15"), 14.4)                                             # 2:30–2:45 どう役立つか
fade(P("s15-15"), P("s14-14"), 0.6)
still(P("s14-14"), 10.8)                                             # 2:45–2:57 既存との違い
fade(P("s14-14"), S("A_overview"), 0.8)
still(S("A_overview"), 1.6, 1.08, 1.0, 0.5, 0.45)                   # 終わり

print("frames", len(frames), "seconds", len(frames) / FPS)
for i, f in enumerate(frames):
    f().save(f"{FR}/{i:05d}.jpg", quality=88)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR}/%05d.jpg",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
                "-movflags", "+faststart", OUT], check=True)
print("saved", OUT)
