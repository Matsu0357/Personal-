"""TikTok のプロフィールアイコンを書き出す。

    python3 make_icon.py  ->  tiktok/icon.png（720x720、丸く切り抜かれる前提で中央に寄せる）
"""
import json
import os
import subprocess

from craftsman import LENS_DEF, craftsman

ROOT = os.path.dirname(os.path.abspath(__file__))
SIZE = 720


def icon_svg():
    # 背景の文字盤（目盛り 12 本）
    ticks = "".join(
        f'<rect x="-6" y="-330" width="12" height="{46 if i % 3 == 0 else 26}" rx="6" '
        f'fill="#8B5A2B" opacity="0.55" transform="rotate({i * 30})"/>' for i in range(12))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
<defs>{LENS_DEF}
<radialGradient id="bg" cx="0.5" cy="0.45" r="0.6">
  <stop offset="0" stop-color="#FFF6E3"/><stop offset="1" stop-color="#F2D9A8"/>
</radialGradient></defs>
<rect width="{SIZE}" height="{SIZE}" fill="url(#bg)"/>
<g transform="translate(360 360)">{ticks}</g>
{craftsman(345, 330, 1.55, "happy")}
</svg>"""


def main():
    out_dir = os.path.join(ROOT, "tiktok")
    svg = os.path.join(out_dir, "icon.svg")
    png = os.path.join(out_dir, "icon.png")
    with open(svg, "w") as f:
        f.write(icon_svg())
    js = """
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: %d, height: %d}});
  await p.goto('file://' + %s); await p.screenshot({path: %s});
  await b.close();
})();""" % (SIZE, SIZE, json.dumps(svg), json.dumps(png))
    subprocess.run(["node", "-e", js], check=True)


if __name__ == "__main__":
    main()
