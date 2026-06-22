#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渲染 QA · 自动出血/空白检测（svg-flowchart-designer 配套）

用途：图生成后必跑，自动揪出靠肉眼容易漏的两类格式问题——
  1) 出血/截断：内容被画布边缘切掉（文字顶到边、卡片超出画布）
  2) 大片空白：画布比内容大一圈，四周有大段无意义留白（skill 老 gotcha）

用法：
  python3 check_render.py a.svg b.png ...        # 自动判断，svg 会先渲成 png
  python3 check_render.py --bleed-band 8 *.svg   # 调边缘检测带宽

依赖：Pillow（必需）；渲染 SVG 需要 chromium/chrome（找不到则只检测已有 png）。
退出码：有问题返回 1，全过返回 0（方便接 CI / 生成脚本里 assert）。
"""
import sys, os, subprocess, tempfile, glob, re

try:
    from PIL import Image
except ImportError:
    print("需要 Pillow: pip install pillow"); sys.exit(2)

CHROMIUM_CANDIDATES = [
    os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
def find_chromium():
    for pat in CHROMIUM_CANDIDATES:
        hits = sorted(glob.glob(pat))
        if hits: return hits[-1]
    return None

def render_svg(svg_path):
    """SVG -> PNG。两个反复踩过的坑都在这里根治：
       ① 包裹层 background 必须匹配 SVG 自身背景，否则 SVG 下方露白，污染裁剪/检测；
       ② chromium 截图会给画布固定多塞一截高度 → 先多渲 120px，再 PIL 自动裁剪到内容边界。"""
    chrome = find_chromium()
    if not chrome:
        print(f"  ⚠ 找不到 chromium，跳过渲染：{svg_path}"); return None
    svg = open(svg_path, encoding="utf-8").read()
    m = re.search(r'<svg[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', svg) or \
        re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        print(f"  ⚠ 读不到 svg 宽高：{svg_path}"); return None
    w, h = int(float(m.group(1))), int(float(m.group(2)))
    bgm = re.search(r'<rect[^>]*\bfill="(#[0-9a-fA-F]{3,6})"', svg)  # 取首个铺满 rect 当背景
    bg = bgm.group(1) if bgm else "#ffffff"
    png = os.path.splitext(svg_path)[0] + ".png"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write("<!doctype html><html><head><meta charset=utf-8><style>"
                f"*{{margin:0;padding:0}}html,body{{background:{bg}}}</style></head><body>" + svg + "</body></html>")
        html = f.name
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=2", f"--window-size={w},{h+120}",
                    f"--screenshot={png}", "file://" + html],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(html)
    if not os.path.exists(png): return None
    try:  # 自动裁剪到内容边界 + 24px 内边距
        from PIL import ImageChops
        im = Image.open(png).convert("RGB")
        diff = ImageChops.difference(im, Image.new("RGB", im.size, im.getpixel((2, 2))))
        bb = diff.getbbox()
        if bb:
            p = 48; W, H = im.size
            im.crop((max(0, bb[0]-p), max(0, bb[1]-p), min(W, bb[2]+p), min(H, bb[3]+p))).save(png)
    except Exception:
        pass
    return png

def detect_bg(im):
    """取四角像素的众数当背景色。"""
    W, H = im.size
    corners = [im.getpixel((1, 1)), im.getpixel((W-2, 1)),
               im.getpixel((1, H-2)), im.getpixel((W-2, H-2))]
    from collections import Counter
    return Counter(corners).most_common(1)[0][0]

def near(px, bg, tol): return all(abs(px[i]-bg[i]) <= tol for i in range(3))

def check(png, band=8, tol=16, blank_warn=0.10):
    im = Image.open(png).convert("RGB"); W, H = im.size
    bg = detect_bg(im); issues = []
    # 1) 出血：四边窄带是否有非背景像素
    edges = {
        "上": [(x, y) for y in range(band) for x in range(0, W, 5)],
        "下": [(x, y) for y in range(H-band, H) for x in range(0, W, 5)],
        "左": [(x, y) for x in range(band) for y in range(0, H, 5)],
        "右": [(x, y) for x in range(W-band, W) for y in range(0, H, 5)],
    }
    for name, pts in edges.items():
        n = sum(0 if near(im.getpixel(p), bg, tol) else 1 for p in pts)
        if n: issues.append(f"{name}边出血({n}点)")
    # 2) 大片空白：从每边往里找第一行/列非背景，留白超过阈值则警告
    def first_content_row(rng, is_row):
        for i in rng:
            line = [im.getpixel((x, i) if is_row else (i, x)) for x in range(0, (W if is_row else H), 5)]
            if any(not near(p, bg, tol) for p in line): return i
        return None
    top = first_content_row(range(H), True); bot = first_content_row(range(H-1, -1, -1), True)
    lft = first_content_row(range(W), False); rgt = first_content_row(range(W-1, -1, -1), False)
    if top is not None:
        for label, gap, total in [("上", top, H), ("下", H-1-bot, H), ("左", lft, W), ("右", W-1-rgt, W)]:
            if gap/total > blank_warn:
                issues.append(f"{label}留白过大({gap}px≈{gap/total:.0%})")
    return bg, issues

def main():
    args = sys.argv[1:]; band = 8
    if "--bleed-band" in args:
        i = args.index("--bleed-band"); band = int(args[i+1]); del args[i:i+2]
    paths = []
    for a in args: paths += sorted(glob.glob(a)) if any(c in a for c in "*?[") else [a]
    bad = 0
    for p in paths:
        if p.lower().endswith(".svg"):
            png = render_svg(p)
            if not png: continue
        else:
            png = p
        bg, issues = check(png, band=band)
        if issues:
            bad += 1; print(f"⚠️  {p}  背景{bg}: " + "，".join(issues))
        else:
            print(f"✅  {p}  四边干净、留白合理")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
