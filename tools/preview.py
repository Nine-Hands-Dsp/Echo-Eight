"""
Apercu de l'interface Eight Echo (sans compiler le plugin) : fond + serigraphie vectorielle (meme Layout que le plugin)
+ footswitches + quelques LED allumees. Sortie : design/preview.png (1235 x 1800) et design/preview_window.png.
Usage : python3 tools/preview.py
"""
import os, re, math, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
pj = json.load(open(os.path.join(HERE, 'print.json')))
S = 2.0                                                   # px par unite du plugin (fond 1235 x 1800)
SS = 3                                                    # sur-echantillonnage du dessin vectoriel
SILK = (230, 236, 241)
FONTS = {'sans': 'LiberationSans-Bold.ttf', 'mono': 'LiberationMono-Bold.ttf'}

bg = Image.open(os.path.join(ROOT, 'background.png')).convert('RGBA')
Wp, Hp = bg.size
canvas = Image.new('RGBA', bg.size, (17, 17, 18, 255)); canvas.alpha_composite(bg)

def paste(fn, cx, cy, size, op=1.0):
    im = Image.open(os.path.join(ROOT, fn)).convert('RGBA')
    n = int(round(size * S)); im = im.resize((n, n), Image.LANCZOS)
    if op < 1: a = np.array(im); a[..., 3] = (a[..., 3] * op).astype(np.uint8); im = Image.fromarray(a)
    canvas.alpha_composite(im, (int(round(cx * S - n / 2)), int(round(cy * S - n / 2))))

def paste_rect(fn, r, op=1.0):
    im = Image.open(os.path.join(ROOT, fn)).convert('RGBA')
    w, h = int(round(r[2] * S)), int(round(r[3] * S)); im = im.resize((w, h), Image.LANCZOS)
    if op < 1: a = np.array(im); a[..., 3] = (a[..., 3] * op).astype(np.uint8); im = Image.fromarray(a)
    canvas.alpha_composite(im, (int(round(r[0] * S)), int(round(r[1] * S))))

# lumiere des LED sur la facade (sous la serigraphie)
G = pj['glows']
paste_rect('glow_tempo.png', G['tempo']); paste_rect('glow_check_red.png', G['check_red'])
paste_rect('glow_slot1.png', G['slot0']); paste_rect('glow_sync.png', G['sync'])

# ------------------------------------------------------------------ serigraphie vectorielle
K = S * SS
ink = Image.new('L', (Wp * SS, Hp * SS), 0); dr = ImageDraw.Draw(ink)
inkx = Image.new('L', (Wp * SS, Hp * SS), 0); drx = ImageDraw.Draw(inkx)     # X2 allume (couleur glace)

def text(s, font, em, track, x, y, rot, d=None, im=None):
    d = d or dr; im = im or ink
    f = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', FONTS[font]), int(round(em * K)))
    widths = [f.getlength(ch) for ch in s]
    total = sum(widths) + track * K * (len(s) - 1)
    if rot == 0:
        cx = x * K - total / 2
        for ch, w in zip(s, widths): d.text((cx, y * K), ch, font=f, fill=255, anchor='lm'); cx += w + track * K
    else:
        hp = int(f.size * 1.6); t = Image.new('L', (int(total) + 8, hp), 0); td = ImageDraw.Draw(t); cx = 4
        for ch, w in zip(s, widths): td.text((cx, hp / 2), ch, font=f, fill=255, anchor='lm'); cx += w + track * K
        t = t.rotate(rot, expand=True)
        im.paste(255, (int(x * K - t.width / 2), int(y * K - t.height / 2)), t)

for t in pj['texts']: text(*t)
# lettrage d'origine : titre (serigraphie) et X2 (allume)
for strokes, wdt, dd in ((pj['title'], pj['titleW'], dr), (pj['x2'], pj['x2W'], drx)):
    for s_ in strokes:
        dd.line([(p[0] * K, p[1] * K) for p in s_], fill=255, width=int(round(wdt * K)), joint='curve')
for (x, y, r) in pj['dots']: dr.ellipse(((x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K), fill=255)
for li, (x0, y0, x1, y1, w) in enumerate(pj['lines']):
    dd = drx if li >= len(pj['lines']) - 2 else dr          # les deux traits de X2 s'allument avec X2
    dd.line((x0 * K, y0 * K, x1 * K, y1 * K), fill=255, width=max(1, int(round(w * K))))
for tr in pj['tris']:
    pts = [(tr[0] * K, tr[1] * K), (tr[2] * K, tr[3] * K), (tr[4] * K, tr[5] * K)]
    dr.line(pts + [pts[0]], fill=255, width=int(round(pj['triStroke'] * K)), joint='curve')

# noms des modes autour du potard MODE (alignes vers l'exterieur), STANDARD choisi
kn = json.load(open(os.path.join(HERE, 'layout.json')))['knobs'][4]
fm = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', FONTS['sans']), int(round(pj['modeFont'] * K)))
for i, nm in enumerate(pj['modeNames']):
    a = math.radians(-135 + 27 * i); s_ = math.sin(a)
    px, py = kn[0] + pj['modeLabelR'] * math.sin(a), kn[1] - pj['modeLabelR'] * math.cos(a)
    anchor = 'lm' if s_ > 0.3 else ('rm' if s_ < -0.3 else 'mm')
    if anchor == 'mm': py -= pj['modeFont'] * 0.45
    (drx if i == 2 else dr).text((px * K, py * K), nm, font=fm, fill=255, anchor=anchor)

# ------------------------------------------------------------------ chemins SVG (motif d'anneaux, logo) : petit lecteur M/L/H/V/C/S/A/Z
def svg_paths(fn):
    src = open(fn).read()
    out = []
    for m in re.finditer(r'<path([^>]*)/?>', src):
        attrs = m.group(1)
        d = re.search(r'\sd="([^"]+)"', attrs).group(1)
        st = re.search(r'stroke="([^"]+)"', attrs); fl = re.search(r'fill="([^"]+)"', attrs); cl = re.search(r'class="([^"]+)"', attrs)
        out.append((d, st.group(1) if st else None, fl.group(1) if fl else None))
    return src, out

def flatten(d):
    toks = re.findall(r'[MmLlHhVvCcSsAaZz]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i = 0; cmd = None; cur = np.array([0.0, 0.0]); start = cur.copy(); last_c = None; polys = []; poly = []
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]): cmd = toks[i]; i += 1
        rel = cmd.islower(); c = cmd.upper()
        if c == 'Z':
            if poly: polys.append(poly); poly = []
            cur = start.copy(); continue
        if c == 'M':
            p = np.array([num(), num()]) + (cur if rel else 0)
            if poly: polys.append(poly)
            poly = [p]; cur = p; start = p.copy(); cmd = 'l' if rel else 'L'; last_c = None; continue
        if c == 'L':
            p = np.array([num(), num()]) + (cur if rel else 0); poly.append(p); cur = p; last_c = None
        elif c == 'H':
            x = num() + (cur[0] if rel else 0); cur = np.array([x, cur[1]]); poly.append(cur); last_c = None
        elif c == 'V':
            y = num() + (cur[1] if rel else 0); cur = np.array([cur[0], y]); poly.append(cur); last_c = None
        elif c in 'CS':
            if c == 'C': c1 = np.array([num(), num()]) + (cur if rel else 0)
            else: c1 = 2 * cur - last_c if last_c is not None else cur.copy()
            c2 = np.array([num(), num()]) + (cur if rel else 0); p = np.array([num(), num()]) + (cur if rel else 0)
            for t in np.linspace(0, 1, 16)[1:]:
                poly.append((1 - t) ** 3 * cur + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * p)
            last_c = c2; cur = p
        elif c == 'A':
            rx, ry, rot, la, sw = num(), num(), num(), num(), num(); p = np.array([num(), num()]) + (cur if rel else 0)
            # cercle (rx = ry, sans rotation dans nos fichiers)
            r = rx; mid = (cur + p) / 2; dv = p - cur; dl = np.linalg.norm(dv)
            h = math.sqrt(max(r * r - (dl / 2) ** 2, 0)); nrm = np.array([-dv[1], dv[0]]) / dl
            cands = [mid + nrm * h, mid - nrm * h]
            def sweep_ok(cc):
                a0 = math.atan2(cur[1] - cc[1], cur[0] - cc[0]); a1 = math.atan2(p[1] - cc[1], p[0] - cc[0])
                da = (a1 - a0) % (2 * math.pi) if sw else -((a0 - a1) % (2 * math.pi))
                return (abs(da) > math.pi) == bool(la), a0, da
            for cc in cands:
                ok, a0, da = sweep_ok(cc)
                if ok: break
            for t in np.linspace(0, 1, 90)[1:]:
                a = a0 + da * t; poly.append(cc + r * np.array([math.cos(a), math.sin(a)]))
            cur = p; last_c = None
    if poly: polys.append(poly)
    return polys

# motif : point gauche du SVG sur le footswitch TAP
mot_src, mot = svg_paths(os.path.join(ROOT, 'assets', 'eight_echo_motif.svg'))
sw_ = float(re.search(r'stroke-width="([\d.]+)"', mot_src).group(1))
ML, MK = pj['motifLeft'], pj['motifScale']; ft = pj['fsTap']
motif = np.zeros((Hp * SS, Wp * SS, 3), np.float32); motif_a = np.zeros((Hp * SS, Wp * SS), np.float32)
for d, stroke, _ in mot:
    col = np.array([int(stroke[1:3], 16), int(stroke[3:5], 16), int(stroke[5:7], 16)], np.float32)
    m = np.zeros((Hp * SS, Wp * SS), np.uint8)
    for poly in flatten(d):
        pts = np.array([[(ft[0] + (q[0] - ML[0]) * MK) * K, (ft[1] + (q[1] - ML[1]) * MK) * K] for q in poly], np.float32)
        cv2.polylines(m, [np.round(pts * 4).astype(np.int32)], False, 255, thickness=max(1, int(round(sw_ * MK * K))), lineType=cv2.LINE_AA, shift=2)
    a = m.astype(np.float32) / 255.0
    motif = motif * (1 - a[..., None]) + col * a[..., None]; motif_a = np.maximum(motif_a, a)

# logo NINE HANDS | DSP
lg_src, lg = svg_paths(os.path.join(ROOT, 'NineHandsLogo.svg'))
vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', lg_src).group(1).split()]
lx, ly, lw = pj['logo']; lk = lw / vb[2]; lh = vb[3] * lk
logo = np.zeros((Hp * SS, Wp * SS, 3), np.float32); logo_a = np.zeros((Hp * SS, Wp * SS), np.float32)
grey_bar = re.findall(r'fill="#919496"', lg_src)
for d, stroke, fill in lg:
    col = np.array([145, 148, 150], np.float32) if fill == '#919496' else np.array([255, 255, 255], np.float32)
    m = np.zeros((Hp * SS, Wp * SS), np.uint8)
    polys = [np.round(np.array([[(lx - lw / 2 + (q[0] - vb[0]) * lk) * K, (ly - lh / 2 + (q[1] - vb[1]) * lk) * K] for q in poly]) * 4).astype(np.int32) for poly in flatten(d)]
    cv2.fillPoly(m, polys, 255, lineType=cv2.LINE_AA, shift=2)
    a = m.astype(np.float32) / 255.0
    logo = logo * (1 - a[..., None]) + col * a[..., None]; logo_a = np.maximum(logo_a, a)

def down(a): return cv2.resize(a, (Wp, Hp), interpolation=cv2.INTER_AREA)
cv = np.asarray(canvas).astype(np.float32)
def comp(col, a):
    global cv
    cv[..., :3] = cv[..., :3] * (1 - a[..., None]) + col * a[..., None]
for g_ in pj['gaps']:
    x0, y0 = int(g_[0] * K), int(g_[1] * K); motif_a[y0:y0 + int(g_[3] * K), x0:x0 + int(g_[2] * K)] = 0
mot_a = down(motif_a) * 0.95; mot_c = down(motif * motif_a[..., None]) / np.maximum(down(motif_a), 1e-4)[..., None]
comp(mot_c, mot_a)
comp(np.array(SILK, np.float32), down(np.asarray(ink, np.float32) / 255.0))
comp(np.array([215, 238, 255], np.float32), down(np.asarray(inkx, np.float32) / 255.0))
la = down(logo_a); comp(down(logo * logo_a[..., None]) / np.maximum(la, 1e-4)[..., None], la * 0.94)
canvas = Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8), 'RGBA')

# footswitches (au-dessus du motif), LED allumees, SYNC allume
sp = pj['sprites']
lay = json.load(open(os.path.join(HERE, 'layout.json')))
for c in (lay['fsTap'], lay['fsBypass']): paste('footswitch.png', c[0], c[1], sp['fs'])
paste('led_ice.png', *lay['ledTempo'], sp['led']); paste('led_red.png', *lay['ledCheck'], sp['led'])
paste_rect('pipe_on.png', pj['pipe'][0] + pj['pipeSize'])
paste('sync_on.png', *lay['sync'], sp['sync'])

# reperes des potards (trait blanc, comme le plugin)
d2 = ImageDraw.Draw(canvas)
R = pj['knobR']
for (k, v) in zip(lay['knobs'], [0.5, 0.5, 0.4, 0.62, None]):
    a = math.radians(-135 + 270 * v) if v is not None else math.radians(-135 + 27 * 2)
    p0 = (k[0] + 0.42 * R * math.sin(a), k[1] - 0.42 * R * math.cos(a)); p1 = (k[0] + 0.88 * R * math.sin(a), k[1] - 0.88 * R * math.cos(a))
    big = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(big)
    bd.line((p0[0] * S + 1, p0[1] * S + 1.4, p1[0] * S + 1, p1[1] * S + 1.4), fill=(0, 0, 0, 110), width=int(0.062 * R * S * 1.15))
    bd.line((p0[0] * S, p0[1] * S, p1[0] * S, p1[1] * S), fill=(236, 240, 243, 255), width=int(0.062 * R * S))
    canvas.alpha_composite(big)

# ligne d'etat
st = pj['statusRect']
fsx = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', FONTS['mono']), int(17.5 * 2 * 1.01))
d2.text(((st[0] + st[2] / 2) * S, (st[1] + st[3] / 2) * S), 'P1  STANDARD  500 MS', font=fsx, fill=SILK + (230,), anchor='mm')

os.makedirs(os.path.join(ROOT, 'design'), exist_ok=True)
canvas.save(os.path.join(ROOT, 'design', 'preview.png'))
# fenetre 60 % (hauteur 493) sur fond sombre
win = Image.new('RGB', canvas.size, (17, 17, 18)); win.paste(canvas, (0, 0), canvas)
win.resize((round(493 * Wp / Hp), 493), Image.LANCZOS).save(os.path.join(ROOT, 'design', 'preview_window.png'))
print('ok', canvas.size)
