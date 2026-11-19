"""動画用にスライドを画像にする。すべての文字を Noto Sans JP に指定し直してから描く
（Yu Gothic がない環境だと、日本語の欄が空のところに中国語フォントが入り、字形が変わるため）。
使い方: python3 render_slides.py 元.pptx 出力フォルダ  → render.pptx を作り、soffice と pdftoppm で画像にする"""
import re, subprocess, sys, zipfile
src, out = sys.argv[1], sys.argv[2]
dst = f"{out}/render.pptx"
zi, zo = zipfile.ZipFile(src), zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for it in zi.infolist():
    d = zi.read(it.filename)
    if it.filename.endswith(".xml"):
        s = d.decode("utf8")
        s = re.sub(r'<a:(latin|ea|cs) typeface="[^"]*"', lambda m: f'<a:{m.group(1)} typeface="Noto Sans JP"', s)
        s = s.replace('lang="en-US"', 'lang="ja-JP"').replace('altLang="en-US"', 'altLang="ja-JP"')
        d = s.encode("utf8")
    zo.writestr(it, d)
zo.close()
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", out, dst], check=True)
for n in (1, 14, 15):  # 動画で使う表紙・既存との違い・どう役立つか
    subprocess.run(["pdftoppm", "-f", str(n), "-l", str(n), "-scale-to-x", "1920", "-scale-to-y", "1080",
                    "-png", f"{out}/render.pdf", f"{out}/s{n}"], check=True)
