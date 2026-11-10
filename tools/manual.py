# EIGHT ECHO (NINE HANDS | DSP) - notice PDF en francais (couverture noire « minimale » commune a toutes les notices).
# Usage : python3 tools/manual.py <dossier des captures (tools/render)> <fichier PDF de sortie>
# Illustrations : captures de la vraie fenetre du plugin (tools/render : eight_echo_exact.png, eight_echo_x2_sync.png,
# eight_echo_mem_modified.png, eight_echo_status.png ; 1236 x 1800 = repere du plugin x 2) ; schemas dans tools/manual/.
import os, sys, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from svgpath import flatten
A = os.path.join(ROOT, "tools", "manual")
SHOTS, OUT = sys.argv[1], sys.argv[2]
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_manual_tmp"); os.makedirs(TMP, exist_ok=True)
VERSION = next(l.split("VERSION")[1].strip(" )\n") for l in open(os.path.join(ROOT, "CMakeLists.txt")) if l.startswith("project("))

DJ = "/usr/share/fonts/truetype/dejavu/"
for n, f in (("R", "DejaVuSans"), ("B", "DejaVuSans-Bold"), ("I", "DejaVuSans-Oblique"), ("M", "DejaVuSansMono-Bold")):
    pdfmetrics.registerFont(TTFont(n, DJ + f + ".ttf"))
pdfmetrics.registerFontFamily("R", normal="R", bold="B", italic="I", boldItalic="B")
FONTS = os.path.join(ROOT, "assets", "fonts")
for n, f in (("Pop", "Poppins-Regular"), ("PopM", "Poppins-Medium"), ("Title", "BarlowCondensed-ExtraBold")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ICE = colors.HexColor("#5FB8F0"); ICE_L = colors.HexColor("#A9DCFF")
DARK = colors.HexColor("#1B2430"); GREY = colors.HexColor("#5E6875"); LIGHT = colors.HexColor("#EAF4FB"); ORANGE = colors.HexColor("#F07A1A")

# ---------------------------------------------------------------- rendu de la pedale (captures du plugin)
def P_(name): return os.path.join(ROOT, name)
LAY = json.load(open(os.path.join(ROOT, "tools", "layout.json")))            # repere du plugin (617,5 x 900)
alpha = Image.open(P_("background.png")).getchannel("A")
def shot(name):
    im = Image.open(os.path.join(SHOTS, name)).convert("RGBA").resize((1235, 1800), Image.LANCZOS)
    im.putalpha(alpha); return im                                             # silhouette du boitier + jacks
base = shot("eight_echo_exact.png"); xs = shot("eight_echo_x2_sync.png"); modi = shot("eight_echo_mem_modified.png")
K = 2.0     # pixels des captures par unite du plugin

def on_white(im):
    w = Image.new("RGB", im.size, (255, 255, 255)); w.paste(im, (0, 0), im); return w
def crop_u(im, x0, y0, x1, y1): return im.crop((int(x0 * K), int(y0 * K), int(x1 * K), int(y1 * K)))

# logo NINE HANDS | DSP blanc (SVG officiel) en PNG
def logo_png(width, path):
    src = open(P_("NineHandsLogo.svg")).read()
    import re
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    k = width / vb[2]; h = int(round(vb[3] * k)); SS = 4
    rgb = np.zeros((h * SS, width * SS, 3), np.float32); a = np.zeros((h * SS, width * SS), np.float32)
    for m in re.finditer(r'<path([^>]*)/?>', src):
        at = m.group(1); d = re.search(r'\sd="([^"]+)"', at).group(1)
        grey = "#919496" in at
        col = np.array([145, 148, 150] if grey else [255, 255, 255], np.float32)
        mk = np.zeros(a.shape, np.uint8)
        polys = [np.round((np.array(pl) - [vb[0], vb[1]]) * k * SS * 4).astype(np.int32) for pl in flatten(d) if len(pl) > 2]
        cv2.fillPoly(mk, polys, 255, lineType=cv2.LINE_AA, shift=2)
        mm_ = mk.astype(np.float32) / 255.0
        rgb = rgb * (1 - mm_[..., None]) + col * mm_[..., None]; a = np.maximum(a, mm_)
    rgb = cv2.resize(rgb, (width, h), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (width, h), interpolation=cv2.INTER_AREA)
    Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), "RGBA").save(path)
LOGO_PNG = os.path.join(TMP, "nine_hands_logo_blanc.png"); logo_png(1200, LOGO_PNG)

# vue d'ensemble annotee
ov = base.resize((base.width * 2 // 3, base.height * 2 // 3), Image.LANCZOS); S = 2.0 * 2 / 3
M = 120
canvas = Image.new("RGB", (ov.width + 2 * M, ov.height + 20), (255, 255, 255)); canvas.paste(ov, (M, 10), ov)
dr = ImageDraw.Draw(canvas)
fb = ImageFont.truetype(DJ + "DejaVuSans-Bold.ttf", 30)
kn = LAY["knobs"]; st_ = LAY["status"]
TARGETS = {1: (kn[0][0], kn[0][1], "L", kn[0][1]), 2: (kn[1][0], kn[1][1], "R", kn[1][1]), 3: (kn[2][0], kn[2][1], "L", kn[2][1]),
           4: (kn[3][0], kn[3][1], "R", kn[3][1]), 5: (kn[4][0], kn[4][1], "R", kn[4][1]), 6: (LAY["slots"][0][0], LAY["slots"][0][1], "L", 160),
           7: (LAY["sync"][0], LAY["sync"][1], "L", LAY["sync"][1]), 8: (LAY["ledTempo"][0], LAY["ledTempo"][1], "L", LAY["ledTempo"][1]),
           9: (LAY["ledCheck"][0], LAY["ledCheck"][1], "R", LAY["ledCheck"][1]), 10: (145.5, 684, "L", 690), 11: (472, 684, "R", 690),
           12: (LAY["fsTap"][0], LAY["fsTap"][1], "L", LAY["fsTap"][1]), 13: (LAY["fsBypass"][0], LAY["fsBypass"][1], "R", LAY["fsBypass"][1] - 30),
           14: (LAY["x2"][0], LAY["x2"][1], "R", 845), 15: (st_[0] + st_[2] - 10, st_[1] + st_[3] / 2, "R", 47)}
OR = (240, 122, 26)
for n, (x, y, side, ly) in TARGETS.items():
    tx, ty = M + x * S, 10 + y * S
    cx = 44 if side == "L" else canvas.width - 44
    cy = 10 + ly * S
    ex = M - 6 if side == "L" else M + ov.width + 6
    dr.line([(cx, cy), (ex, cy), (tx, ty)], fill=OR, width=4)
    dr.ellipse((tx - 7, ty - 7, tx + 7, ty + 7), fill=OR)
    dr.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=OR)
    dr.text((cx, cy + 1), str(n), font=fb, fill=(255, 255, 255), anchor="mm")
ov_img = os.path.join(TMP, "overview.png"); canvas.save(ov_img)

# memoires : tubes 1-7 (memoire 1 rappelee) et memoire 3 modifiee
def strip(im): return on_white(crop_u(im, 18, 20, 118, 420))
m1, m2 = strip(base), strip(modi)
mem = Image.new("RGB", (m1.width * 2 + 30, m1.height), (255, 255, 255)); mem.paste(m1, (0, 0)); mem.paste(m2, (m1.width + 30, 0))
mem_img = os.path.join(TMP, "memories.png"); mem.save(mem_img)

# pastille : barre de presets et ligne d'etat
r_ = st_
bar = Image.new("RGB", (int(r_[2] * K) + 40, int(r_[3] * K) * 2 + 60), (255, 255, 255))
bar.paste(on_white(crop_u(base, r_[0] - 10, r_[1] - 7, r_[0] + r_[2] + 10, r_[1] + r_[3] + 7)), (0, 0))
bar.paste(on_white(crop_u(shot("eight_echo_status.png"), r_[0] - 10, r_[1] - 7, r_[0] + r_[2] + 10, r_[1] + r_[3] + 7)), (0, int(r_[3] * K) + 40))
bar_img = os.path.join(TMP, "bar.png"); bar.save(bar_img)

# vignettes (sprites du plugin sur la facade)
def thumb(im, box, size=180):
    c = on_white(crop_u(im, *box)); return c.resize((size, int(size * c.height / c.width)), Image.LANCZOS)
sl = LAY["slots"][0]
th_mem = thumb(base, (18, sl[1] - 30, 80, sl[1] + 22)); th_mem_path = os.path.join(TMP, "th_mem.png"); th_mem.save(th_mem_path)
sy = LAY["sync"]
th_sync = thumb(xs, (sy[0] - 34, sy[1] - 34, sy[0] + 34, sy[1] + 34)); th_sync_path = os.path.join(TMP, "th_sync.png"); th_sync.save(th_sync_path)
x2c = LAY["x2"]
x2_img = os.path.join(TMP, "x2.png"); thumb(xs, (x2c[0] - 60, x2c[1] - 30, x2c[0] + 60, x2c[1] + 30), 360).save(x2_img)
lc = LAY["ledCheck"]; ltp = LAY["ledTempo"]
bgimg = Image.open(P_("background.png")).convert("RGBA")
def lens(sprite, c, path):
    box = (int((c[0] - 16) * K), int((c[1] - 16) * K), int((c[0] + 16) * K), int((c[1] + 16) * K))
    im = bgimg.crop(box)
    if sprite:
        sp = Image.open(P_(sprite)).convert("RGBA"); n = int(round(LAY.get("ledS", 27.81) * K)); sp = sp.resize((n, n), Image.LANCZOS)
        im.alpha_composite(sp, ((im.width - n) // 2, (im.height - n) // 2))
    on_white(im).save(path); return path
LENS = {"lens_red": lens("led_red.png", lc, os.path.join(TMP, "lens_red.png")), "lens_off": lens(None, lc, os.path.join(TMP, "lens_off.png")),
        "lens_green": lens("led_green.png", lc, os.path.join(TMP, "lens_green.png")), "lens_orange": lens("led_orange.png", lc, os.path.join(TMP, "lens_orange.png")),
        "lens_ice": lens("led_ice.png", ltp, os.path.join(TMP, "lens_ice.png"))}

# footswitchs : vue annotee de la partie basse
fsv = crop_u(base, 18, 600, 600, 900)
fsv = on_white(fsv)
FM = 260
fc = Image.new("RGB", (fsv.width + 2 * FM, fsv.height), (255, 255, 255)); fc.paste(fsv, (FM, 0))
d2 = ImageDraw.Draw(fc); fl = ImageFont.truetype(DJ + "DejaVuSans-Bold.ttf", 22)
def lab(x, y, text, side, ly):
    tx, ty = FM + (x - 18) * K, (y - 600) * K
    ex = FM - 8 if side == "L" else FM + fsv.width + 8
    tx0 = 10 if side == "L" else FM + fsv.width + 20
    d2.line([(ex, ly), (tx, ty)], fill=OR, width=3); d2.ellipse((tx - 6, ty - 6, tx + 6, ty + 6), fill=OR)
    d2.text((FM - 14 if side == "L" else FM + fsv.width + 14, ly), text, font=fl, fill=(27, 36, 48), anchor="rm" if side == "L" else "lm")
lab(ltp[0], ltp[1], "LED de tempo", "L", 50); lab(145.5, 684, "Mémoire précédente", "L", 170)
lab(LAY["fsTap"][0], LAY["fsTap"][1], "TAP", "L", 370)
lab(lc[0], lc[1], "LED CHECK", "R", 50); lab(472, 684, "Mémoire suivante", "R", 170)
lab(LAY["fsBypass"][0], LAY["fsBypass"][1], "BYPASS", "R", 330); lab(x2c[0], x2c[1], "X2 (delay long)", "R", 450)
fs_img = os.path.join(TMP, "footswitches.png"); fc.save(fs_img)

# couverture : pedale detouree, reflet au sol, halo bleu glace tres doux (geometrie : pad = 16 % de la largeur)
cut = base.crop(base.getbbox()); cw, ch = cut.size; pad = int(cw * 0.16)
cv = Image.new("RGBA", (int(cw * 1.32), int(ch * 1.2) + pad), (0, 0, 0, 255))
ox = (cv.width - cw) // 2
yy, xx = np.mgrid[0:cv.height, 0:cv.width].astype(np.float64)
glow = np.exp(-(((xx - cv.width / 2) / (cw * 0.62)) ** 2 + ((yy - (pad + ch * 0.45)) / (ch * 0.5)) ** 2)) * 38
edge = np.clip(np.minimum.reduce([xx, cv.width - 1 - xx, yy, cv.height - 1 - yy]) / (pad * 0.9), 0, 1); glow *= edge ** 2
cv = Image.alpha_composite(cv, Image.fromarray(np.dstack([glow * 0.37, glow * 0.72, glow * 0.94, np.full_like(glow, 255)]).astype(np.uint8), "RGBA"))
refl = np.array(cut.transpose(Image.FLIP_TOP_BOTTOM)).astype(np.float64)
refl[..., 3] *= (np.clip(1 - np.arange(ch) / (ch * 0.22), 0, 1) ** 1.6 * 0.22)[:, None]
cv.alpha_composite(Image.fromarray(refl.astype(np.uint8), "RGBA"), (ox, pad + ch + 4)); cv.alpha_composite(cut, (ox, pad))
cover_img = os.path.join(TMP, "cover.png"); cv.convert("RGB").save(cover_img)
COVER_GEOM = (cw, ch, pad)

def img(path, width):
    im = Image.open(path); return RLImage(path, width=width, height=width * im.height / im.width)

# ---------------------------------------------------------------- styles
st = {
    "h1": ParagraphStyle("h1", fontName="B", fontSize=16, leading=20, textColor=DARK, spaceBefore=8, spaceAfter=7, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="B", fontSize=10.5, leading=14, textColor=colors.HexColor("#2A7FC0"), spaceBefore=6, spaceAfter=2, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="R", fontSize=9.2, leading=13.4, textColor=DARK, spaceAfter=5),
    "cap": ParagraphStyle("cap", fontName="I", fontSize=7.8, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="R", fontSize=8.2, leading=10.8, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="B", fontSize=8.2, leading=10.8, textColor=DARK),
    "hcell": ParagraphStyle("hcell", fontName="B", fontSize=8.2, leading=10.8, textColor=colors.white),
    "note": ParagraphStyle("note", fontName="R", fontSize=8.8, leading=12.6, textColor=DARK),
    "num": ParagraphStyle("num", fontName="B", fontSize=9, leading=11, textColor=colors.white, alignment=TA_CENTER),
    "cover": ParagraphStyle("cover", fontName="B", fontSize=30, leading=36, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="R", fontSize=10.5, leading=15, textColor=colors.HexColor("#C9CED6"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="B", fontSize=8.5, leading=11, textColor=ICE_L),
}
def P(t, s="p"): return Paragraph(t, st[s])
W = A4[0] - 36 * mm
def bullets(items): return [P("&bull;&nbsp;&nbsp;" + i) for i in items]
def table(rows, widths, header=True, first_bold=True):
    data = [[P(c, "hcell" if (header and r == 0) else ("cellb" if (first_bold and ci == 0) else "cell")) for ci, c in enumerate(row)] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    s = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5DEE6")),
         ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header: s += [("BACKGROUND", (0, 0), (-1, 0), DARK)]
    s += [("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F6F9FC")) for r in range(2 if header else 1, len(rows), 2)]
    t.setStyle(TableStyle(s)); return t
def note(t):
    tb = Table([[P(t, "note")]], colWidths=[W]); tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 2.5, ICE),
                                                                     ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return KeepTogether([Spacer(1, 2), tb, Spacer(1, 5)])
def numbered(rows):
    data = []
    for n, t in rows:
        b = Table([[P(str(n), "num")]], colWidths=[6 * mm], rowHeights=[6 * mm])
        b.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ORANGE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        data.append([b, P(t)])
    tb = Table(data, colWidths=[9 * mm, W - 9 * mm]); tb.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return tb

# ---------------------------------------------------------------- donnees (code livre : PluginProcessor.cpp)
PRESETS = [("Clean Slapback", "STANDARD"), ("Rockabilly Tape", "TAPE"), ("Doubler", "STANDARD"), ("Bread & Butter", "STANDARD"),
           ("Dotted 8th Arena", "STANDARD"), ("Ping Pong Eighths", "STANDARD"), ("BBD Crunch Lead", "ANALOG"), ("Dark BBD Wash", "ANALOG"),
           ("Floating Tape Solo", "TAPE"), ("Long Tape Ambience", "TAPE"), ("Soft Ballad", "WARM"), ("Jazz Room", "WARM"),
           ("Lush Chorus Echo", "MOD"), ("80s Stereo Lead", "MOD"), ("Echo Hall", "+RV"), ("Cathedral", "+RV"), ("Heaven Swell", "SHIM"),
           ("Octave Haze", "SHIM"), ("Dream Swell (hold)", "WARP"), ("Space Freeze (hold)", "WARP"), ("Backwards Solo", "REVERSE"),
           ("Backwards Pad", "REVERSE"), ("Machine Gun (hold)", "GLT"), ("Stutter Groove (hold)", "GLT"), ("Granular Buzz (hold)", "GLT"), ("Looper", "LOOP")]
MODES_T = [("LOOP", "40 s (20 s stereo)<br/>40 s"), ("ANALOG", "20–800 ms<br/>40–1600 ms"), ("STANDARD", "20–800 ms<br/>40–1600 ms"),
           ("TAPE", "20–800 ms<br/>40–1600 ms"), ("WARM", "20–800 ms<br/>40–1600 ms"), ("REVERSE", "300–5000 ms<br/>600–10000 ms"),
           ("+RV", "20–800 ms<br/>40–1600 ms"), ("SHIM", "200–800 ms<br/>400–1600 ms"), ("MOD", "20–800 ms<br/>40–1600 ms"),
           ("WARP", "20–800 ms<br/>40–1600 ms"), ("GLT", "10–400 ms<br/>20–800 ms")]
MIDI_ROWS = [("E.LEVEL", 20, "cont"), ("MIX", 21, "cont"), ("FEEDBACK", 22, "cont"), ("TIME", 23, "cont"), ("MODE", 24, "sel"),
             ("X2", 25, "tog"), ("SYNC", 26, "tog"), ("EXP", 27, "exp"), ("BYPASS", 80, "fs"), ("TAP", 81, "tap"),
             ("PREV MEMORY", 82, "act"), ("NEXT MEMORY", 83, "act")]

from manual_text import T   # textes EN / FR (tools/manual_text.py)

# ---------------------------------------------------------------- mise en page
def section(lang):
    t = T[lang]; f = [NextPageTemplate("p"), PageBreak()]
    f.append(P(t["toc_t"], "h1"))
    toc = [[P(a, "cell"), P(b, "cell")] for a, b in zip(t["toc"][:9], t["toc"][9:] + [""])]
    tt = Table(toc, colWidths=[W / 2, W / 2]); tt.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    f.append(tt)
    f.append(P(t["s1"], "h1")); f += [P(x) for x in t["intro"]]
    f.append(P(t["s2"], "h1")); f += bullets(t["inst"]); f.append(P(t["where_h"], "h2")); f.append(P(t["where"]))
    f.append(PageBreak())
    f.append(P(t["s3"], "h1")); f.append(img(ov_img, W * 0.70)); f.append(P(t["ov_cap"], "cap"))
    f.append(numbered(t["ov"]))
    f.append(KeepTogether([img(bar_img, W * 0.62), P("La pastille du haut : barre de presets au repos (mémoire 1 · Bread &amp; Butter), ligne d'état pendant un réglage (E.LEVEL 64 %).", "cap")]))
    f.append(P(t["s4"], "h1"))
    for h, x in t["knobs"]: f.append(P(h, "h2")); f.append(P(x))
    f.append(note(t["mouse"]))
    f.append(CondPageBreak(110 * mm))
    f.append(P(t["s5"], "h1")); f.append(img(os.path.join(A, "modes_dial.png"), W * 0.48)); f.append(P(t["dial_cap"], "cap"))
    rows = [t["modes_hdr"]] + [[m, r, t["modes"][i][0], t["modes"][i][1]] for i, (m, r) in enumerate(MODES_T)]
    f.append(table(rows, [20 * mm, 26 * mm, W - 46 * mm - 44 * mm, 44 * mm]))
    f.append(P(t["s6"], "h1")); f.append(P(t["fs_intro"]))
    f.append(img(fs_img, W)); f.append(P(t["fs_cap"], "cap"))
    f.append(table(t["fs_rows"], [30 * mm, 38 * mm, 50 * mm, W - 118 * mm]))
    f.append(note(t["tempo_mode"]))
    f.append(P(t["s7"], "h1"))
    icons = [("lens_red", 0), ("lens_off", 1), ("lens_green", 2), ("lens_orange", 3), ("lens_red", 4), ("lens_green", 5), ("lens_ice", 6)]
    rows = [[P(t["led_hdr"][0], "hcell"), P(t["led_hdr"][1], "hcell"), P(t["led_hdr"][2], "hcell")]]
    for nm, i in icons:
        rows.append([RLImage(LENS[nm], width=8 * mm, height=8 * mm), P(t["leds"][i][0], "cellb"), P(t["leds"][i][1], "cell")])
    rows.append([RLImage(th_mem_path, width=12 * mm, height=12 * mm * th_mem.height / th_mem.width), P(t["leds"][7][0], "cellb"), P(t["leds"][7][1], "cell")])
    rows.append([RLImage(th_sync_path, width=8 * mm, height=8 * mm), P(t["leds"][8][0], "cellb"), P(t["leds"][8][1], "cell")])
    rows.append([RLImage(x2_img, width=14 * mm, height=14 * mm * 180 / 360), P("X2", "cellb"), P(t["x2"], "cell")])
    lt = Table(rows, colWidths=[16 * mm, 36 * mm, W - 52 * mm])
    lt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BACKGROUND", (0, 0), (-1, 0), DARK), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5DEE6")),
                            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    f.append(lt)
    f.append(CondPageBreak(120 * mm))
    f.append(P(t["s8"], "h1"))
    mt = Table([[img(mem_img, 52 * mm), [P(x) for x in t["mem"]] + [P(t["mem_cap"], "cap")]]], colWidths=[56 * mm, W - 56 * mm])
    mt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)])); f.append(mt)
    f.append(P(t["s9"], "h1")); f += [P(x) for x in t["tempo"]]
    f.append(img(os.path.join(A, "taps_" + lang + ".png"), W * 0.78)); f.append(P(t["taps_cap"], "cap"))
    f.append(P(t["s10"], "h1")); f += bullets(t["twist"])
    f.append(P(t["s11"], "h1")); f += [P(x) for x in t["looper"]]
    f.append(img(os.path.join(A, "looper_" + lang + ".png"), W * 0.72)); f.append(P(t["looper_cap"], "cap")); f.append(note(t["loop_note"]))
    f.append(P(t["s12"], "h1")); f.append(img(os.path.join(A, "stereo.png"), W * 0.70)); f.append(P(t["stereo_cap"], "cap")); f += bullets(t["stereo"])
    f.append(P(t["s13"], "h1")); f += bullets(t["menu"]); f.append(P(t["win_h"], "h2")); f.append(P(t["win"]))
    f.append(CondPageBreak(150 * mm))
    f.append(P(t["s14"], "h1")); f.append(P(t["midi_intro"]))
    rows = [t["midi_hdr"]] + [[n, t["learn_where_exp"] if k == "exp" else t["learn_where"], t["types"][k]] for n, c, k in MIDI_ROWS]
    f.append(table(rows, [30 * mm, 38 * mm, W - 68 * mm]))
    f.append(P(t["learn_h"], "h2")); f.append(numbered(list(enumerate(t["learn"], 1))))
    f += bullets(t["learn_more"])
    f.append(P(t["auto_h"], "h2")); f.append(P(t["auto"]))
    f.append(CondPageBreak(160 * mm))
    f.append(P(t["s15"], "h1"))
    f.append(table([t["pre_hdr"]] + [[n, m, t["pre"][i]] for i, (n, m) in enumerate(PRESETS)], [40 * mm, 22 * mm, W - 62 * mm]))
    f.append(P(t["pre_cap"], "cap"))
    f.append(CondPageBreak(140 * mm))
    f.append(P(t["s16"], "h1")); f.append(img(os.path.join(A, "signal_flow.png"), W * 0.82)); f.append(P(t["flow_cap"], "cap"))
    f.append(KeepTogether([table(t["spec"], [34 * mm, W - 34 * mm], header=False)]))
    f.append(P(t["s17"], "h1")); f += bullets(t["trouble"])
    f.append(PageBreak())
    return f

def deco(lang):
    def _d(c, doc):
        t = T[lang]; c.saveState()
        c.setFillColor(DARK); c.rect(0, A4[1] - 11 * mm, A4[0], 11 * mm, stroke=0, fill=1)
        c.setFillColor(ICE); c.rect(0, A4[1] - 11.8 * mm, A4[0], 0.8 * mm, stroke=0, fill=1)
        c.drawImage(LOGO_PNG, 18 * mm, A4[1] - 7.6 * mm, width=32 * mm, height=32 * mm * 244 / 2602, mask="auto")
        c.setFont("R", 7.5); c.setFillColor(colors.HexColor("#C9D3DD")); c.drawRightString(A4[0] - 18 * mm, A4[1] - 7 * mm, "EIGHT ECHO · " + t["hdr"])
        c.setFillColor(GREY); c.drawString(18 * mm, 10 * mm, "Eight Echo (NINE HANDS | DSP) · v" + VERSION)
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page)); c.restoreState()
    return _d

# ---- Couverture « minimale » (modele 6, valide nov. 2026) : gabarit fixe commun a toutes les notices ----
# Mesures en mm depuis le HAUT de la page A4, sauf le logo et le bandeau (depuis le bas). Aucun autre element.
COVER_NAME, COVER_SUB = "EIGHT ECHO", "Delay numérique"
PEDAL_H, PEDAL_MAXW, PEDAL_TOP = 82 * mm, 115 * mm, 84 * mm
LANG_TOP = 18 * mm
NAME_TOP, NAME_PT = 194 * mm, 30
SUB_TOP, SUB_PT = 208 * mm, 10
LOGO_W, LOGO_BOTTOM = 38 * mm, 22 * mm
BAND_H = 3 * mm
def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ICE); c.rect(0, 0, A4[0], BAND_H, stroke=0, fill=1)
    def line(text, top, font, size, cs, col):
        w = pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)
        tt = c.beginText((A4[0] - w) / 2, A4[1] - top - size * 0.8); tt.setFont(font, size); tt.setCharSpace(cs)
        tt.setFillColor(col); tt.textOut(text); c.drawText(tt)
    line("FRANÇAIS", LANG_TOP, "PopM", 8.5, 0, ICE_L)
    iw, ih = Image.open(cover_img).size; cw, ch, pad = COVER_GEOM
    k = min(PEDAL_H / ch, PEDAL_MAXW / cw)
    dw, dh = iw * k, ih * k
    y0 = A4[1] - (PEDAL_TOP + (PEDAL_H - ch * k) / 2) + pad * k
    c.drawImage(cover_img, (A4[0] - dw) / 2, y0 - dh, dw, dh)
    line(COVER_NAME, NAME_TOP - NAME_PT * 0.02, "Title", NAME_PT, NAME_PT * 0.5, colors.white)
    line(COVER_SUB, SUB_TOP, "Pop", SUB_PT, 1.5, colors.HexColor("#BDC4B8"))
    lw, lh = Image.open(LOGO_PNG).size
    c.drawImage(LOGO_PNG, (A4[0] - LOGO_W) / 2, LOGO_BOTTOM, LOGO_W, LOGO_W * lh / lw, mask="auto")
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=17 * mm,
                      title="EIGHT ECHO - Notice v" + VERSION, author="NINE HANDS | DSP")
fr_ = lambda i: Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id=i)
doc.addPageTemplates([PageTemplate(id="cover", frames=[fr_("c")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[fr_("p")], onPage=deco("fr"))])
fr = section("fr")
doc.build(fr[:-1])
print(OUT, VERSION)
