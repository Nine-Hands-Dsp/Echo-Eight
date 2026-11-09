"""
EIGHT ECHO (NINE HANDS | DSP) - visuel du plugin, entierement synthetise (v2.0, nov. 2026).

Regle NINE HANDS | DSP des pedales simples : image du plugin de 1235 x 1800 pixels, pedale plein cadre (le boitier touche
le haut et le bas de l'image, les jacks touchent les bords gauche et droit), fond transparent seulement autour des jacks.
Boitier : aluminium brosse anodise bleu ardoise (teinte de la pedale d'origine Eight Echo), rendu en 4K (repere de travail
760 x 958 unites a 4 px par unite = 3040 x 3832 px) puis ramene a 1235 x 1800.
Pieces photo du kit NINE HANDS | DSP (tools/photo_controls.py) : potards noirs en aluminium tourne, LED a lentille facettee
(rouge d'origine, recoloree en bleu glace / vert / orange), footswitch d'Echoflex, embases jack (OUT a gauche, IN a droite).
Une seule lumiere pour toute la pedale : en haut a gauche (ombres portees vers le bas a droite).

Textes, graduations, traits, triangles, motif d'anneaux (assets/eight_echo_motif.svg) et logo NINE HANDS | DSP
(NineHandsLogo.svg) ne sont PAS imprimes dans le fond : le plugin les dessine en vectoriel (Layout.h), nets a toute taille.

Sorties (racine du depot) :
  background.png      fond 1235 x 1800 RGBA (boitier, potards sans repere, LED eteintes, bouton SYNC eteint, jacks)
  footswitch.png      footswitch (photo Echoflex) avec son ombre, dessine par le plugin PAR-DESSUS le motif d'anneaux
  fs_refl.png         reflet (blanc, canal alpha) de la LED voisine sur le flanc de l'ecrou, teinte par le plugin
  led_*.png           lentilles allumees (glace, rouge, vert, orange ; petite = memoires 1-7)
  glow_*.png          facade eclairee par chaque LED (canal alpha = seule la lumiere ajoutee)
  sync_on.png         capuchon du bouton SYNC allume
  Layout.h, tools/layout.json, design/preview_art.png
Usage : python3 tools/make_art.py
"""
import os, sys, math, json
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import photo_controls as PC

AS = 4                                   # pixels par unite : boitier rendu en 4K
UW, UH = 760, 958
W, H = UW * AS, UH * AS

L = np.array([-0.46, -0.62, 0.64]); L /= np.linalg.norm(L)        # vers la lumiere (x droite, y bas, z vers l'oeil)
V = np.array([0.0, 0.0, 1.0]); HV = (L + V) / np.linalg.norm(L + V)

# ------------------------------------------------------------------ geometrie (unites de travail)
OUT_W, OUT_H = 1235, 1800
JACK_LEN = 92.0                                  # deux embases par tranche (A et B, comme la pedale d'origine)
_jt = PC.jack_sprite(JACK_LEN, 1, 1)
JACK_PROT = _jt[1] - 0.5                         # saillie de l'embase hors du boitier
PY0, PH, PR = 34.0, 890.0, 30.0
PW = OUT_W / OUT_H * PH - 2 * JACK_PROT          # boitier + jacks = largeur de l'image (meme echelle que la hauteur)
PX0 = (UW - PW) / 2
CX = PX0 + PW / 2
CROP_X0, CROP_W = PX0 - JACK_PROT, PW + 2 * JACK_PROT
SC = (OUT_H / 2.0) / PH                          # unites de travail -> unites du plugin (617,5 x 900)

# placement repris de la pedale Eight Echo d'origine (visuel 578 x 896, boitier x 27-551, y 18-886)
KY = PH / 868.0
KXo = PW / 524.0
def P(xo, yo): return (CX + (xo - 289.0) * KXo, PY0 + (yo - 18.0) * KY)

KNOB_R = 52.0
KNOBS = [('elevel', 'E.LEVEL') + P(204, 149), ('mix', 'MIX') + P(394.5, 149),
         ('feedback', 'FEEDBACK') + P(204, 311), ('time', 'TIME') + P(394.5, 311), ('mode', 'MODE') + P(396.5, 497)]
LABEL_DY = 82.0                                  # etiquette sous le potard
SLOT_X = P(52, 0)[0]; SLOT_NUM_X = P(86, 0)[0]
SLOTS = [P(52, y)[1] for y in (124, 175, 228, 279, 331, 383, 435)]
SLOT_LENS = 7.5
SYNC = P(204, 491.5); SYNC_CAP, SYNC_BEZ = 22.0, 28.0
LED_T = P(144.5, 621.0); LED_C = P(434.2, 620.0); LED_LENS = 11.0
TITLE1, TITLE2 = P(289, 611), P(289, 648)
TRI_UP, TRI_DN = P(141, 679), P(436, 677)
FS_T, FS_B = P(143, 775), P(438, 775)
FS_FLATS = 98.0
X2 = (CX, FS_T[1] + 2.0)
FS_LABEL_Y = P(0, 860)[1]
LOGO_C = (CX, P(0, 861)[1]); LOGO_W = 186.0
JACK_YS = [P(0, 480)[1], P(0, 622)[1]]           # A, B
STATUS = (CX - 210.0 * KXo, P(0, 42)[1], 420.0 * KXo, 30.0)

# ------------------------------------------------------------------ outils
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
UX, UY = (XX + 0.5) / AS, (YY + 0.5) / AS
del YY, XX

def rrect_sd(x, y, x0, y0, w, h, r):
    cx, cy = x0 + w / 2, y0 + h / 2
    qx = np.abs(x - cx) - (w / 2 - r); qy = np.abs(y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def fbm(shape, scales, amps, seed=0):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32)
    for s, a in zip(scales, amps):
        n = r.standard_normal((max(2, shape[0] // s + 2), max(2, shape[1] // s + 2))).astype(np.float32)
        out += a * cv2.resize(n, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)
    return out

def over(dst, rgba, x0, y0):
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x0)), int(round(y0))
    sx0, sy0 = max(0, -X0), max(0, -Y0)
    ex, ey = min(w, W - X0), min(h, H - Y0)
    a = rgba[sy0:ey, sx0:ex, 3:4] / 255.0
    reg = dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex]
    dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = reg * (1 - a) + rgba[sy0:ey, sx0:ex, :3] * a

# ------------------------------------------------------------------ 1. boitier : aluminium brosse anodise bleu ardoise, arete arrondie
print('boitier 4K...')
sd = rrect_sd(UX, UY, PX0, PY0, PW, PH, PR)
body = np.clip(0.5 - sd * AS, 0, 1).astype(np.float32)
EDGE = 9.0
d_in = np.clip(-sd, 0, None)
hgt = np.where(d_in < EDGE, np.sqrt(np.clip(EDGE ** 2 - (EDGE - d_in) ** 2, 0, None)), EDGE).astype(np.float32)
del d_in
gy, gx = np.gradient(cv2.GaussianBlur(hgt, (0, 0), 1.0 * AS / 2), 1.0 / AS)
del hgt
nrm = np.dstack([-gx, -gy, np.ones_like(gx)]).astype(np.float32); del gx, gy
nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ndl = np.clip(nrm @ L.astype(np.float32), 0, 1); ndh = np.clip(nrm @ HV.astype(np.float32), 0, 1); del nrm
paint = np.array([86.0, 103.0, 116.0], np.float32)            # bleu ardoise de la pedale d'origine
# brossage horizontal : bruit tres allonge dans le sens x (stries fines + bandes plus larges), a 4 px par unite
rng = np.random.default_rng(3)
def streaks(sig_y, len_x, amp, seed):
    n = np.random.default_rng(seed).standard_normal((H, W // 8 + 2)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)
    n = cv2.GaussianBlur(n, (0, 0), sigmaX=len_x * AS, sigmaY=sig_y * AS)
    return n / (n.std() + 1e-6) * amp
brush = streaks(0.12, 9.0, 5.0, 31) + streaks(0.45, 40.0, 3.5, 32) + streaks(2.5, 120.0, 2.0, 33)
# reflet anisotrope du metal brosse : large bande claire (la lumiere en haut a gauche glisse le long du brossage)
sheen = np.exp(-(((UY - (PY0 + 0.24 * PH)) / (0.30 * PH)) ** 2)) * (0.75 + 0.25 * np.exp(-((UX - (PX0 + 0.3 * PW)) / (0.7 * PW)) ** 2))
sheen = sheen.astype(np.float32)
spec_tint = np.array([0.92, 0.97, 1.0], np.float32)
encl = paint * (0.62 + 0.52 * ndl)[..., None]
encl += (brush * (0.65 + 0.7 * sheen))[..., None] * np.array([0.92, 0.98, 1.04], np.float32)
encl += (26.0 * sheen)[..., None] * spec_tint
encl += (70 * ndh ** 50 + 16 * ndh ** 6)[..., None] * spec_tint
encl += fbm((H, W), [2, 7], [1.1, 0.6], 4)[..., None]          # grain fin de l'anodisation
del ndl, ndh, brush
# leger degrade : un peu plus sombre en bas a droite (lumiere en haut a gauche)
encl *= (1.04 - 0.10 * np.clip((UX - PX0) / PW * 0.4 + (UY - PY0) / PH * 0.6, 0, 1))[..., None]
img = encl * body[..., None]
del encl

# ------------------------------------------------------------------ 2. occlusion douce autour des elements en relief
print('commandes...')
def occlusion(mask, strength=1.0):
    contact = cv2.GaussianBlur(mask, (0, 0), 3.0 * AS)
    soft = cv2.GaussianBlur(mask, (0, 0), 12.0 * AS)
    o = np.clip(contact * 0.5 + soft * 0.8, 0, 0.45) * strength * (1.0 - mask)
    img[...] = img * (1.0 - o * body)[..., None]
m_ = np.zeros((H, W), np.float32)
for (_, _, x, y) in KNOBS:
    m_ = np.maximum(m_, np.clip((KNOB_R - np.hypot(UX - x, UY - y)) * AS, 0, 1))
m_ = np.maximum(m_, np.clip((SYNC_BEZ - np.hypot(UX - SYNC[0], UY - SYNC[1])) * AS, 0, 1))
occlusion(m_)
del m_

# ------------------------------------------------------------------ 3. potards (photo du kit, repere efface : seul le repere du plugin tourne)
for (_, _, x, y) in KNOBS:
    KN, KS = PC.knob_sprite(KNOB_R, AS)
    over(img, KN, (x - KS / 2) * AS, (y - KS / 2) * AS)

# ------------------------------------------------------------------ 4. LED eteintes (photo du kit) + lentilles allumees
LEDS = {}
def led(name, R, colour):
    off, on, S_ = PC.led_sprites(R, AS, colour=colour)
    LEDS[name] = (on, S_)
    return off, S_
for c, rl in ((LED_T, None), (LED_C, None)):
    pass
off, S_ = led('led_ice', LED_LENS, 'ice'); over(img, off, (LED_T[0] - S_ / 2) * AS, (LED_T[1] - S_ / 2) * AS)
off, S_ = led('led_red', LED_LENS, 'red'); over(img, off, (LED_C[0] - S_ / 2) * AS, (LED_C[1] - S_ / 2) * AS)
led('led_green', LED_LENS, 'green'); led('led_orange', LED_LENS, 'orange')
offS, SS_ = led('led_slot', SLOT_LENS, 'ice')
for y in SLOTS:
    over(img, offS, (SLOT_X - SS_ / 2) * AS, (y - SS_ / 2) * AS)

# ------------------------------------------------------------------ 5. bouton SYNC : bague chromee + capuchon en acrylique depoli
def sync_sprites():
    S_ = SYNC_BEZ * 2.9
    n = int(round(S_ * AS))
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / AS
    # hauteurs : bague torique entre le capuchon et le bord, capuchon legerement bombe
    rb0, rb1 = SYNC_CAP + 0.6, SYNC_BEZ
    mid, half = (rb0 + rb1) / 2, (rb1 - rb0) / 2
    tor = np.sqrt(np.clip(1 - ((r - mid) / half) ** 2, 0, 1)) * 3.2
    cap = 1.6 + 2.6 * np.clip(1 - (r / SYNC_CAP) ** 2, 0, 1)
    h_ = np.where(r <= SYNC_CAP, cap, np.where(r <= rb1, tor, 0)).astype(np.float32)
    gy_, gx_ = np.gradient(cv2.GaussianBlur(h_, (0, 0), 0.6 * AS / 2), 1.0 / AS)
    nn = np.dstack([-gx_, -gy_, np.ones_like(gx_)]); nn /= np.linalg.norm(nn, axis=2, keepdims=True)
    nl = np.clip(nn @ L, 0, 1); nh = np.clip(nn @ HV, 0, 1)
    # chrome : environnement (sol sombre / ciel clair selon la normale) + reflet vif
    env = 0.5 + 0.5 * (-nn[..., 1] * 0.7 - nn[..., 0] * 0.3)
    chrome = (60 + 150 * env ** 1.4)[..., None] * np.array([0.95, 0.98, 1.0]) + (255 * nh ** 60)[..., None]
    # capuchon depoli eteint : gris bleute, diffusion douce, grain fin
    gr = np.random.default_rng(8).standard_normal((n, n)).astype(np.float32)
    gr = cv2.GaussianBlur(gr, (0, 0), 0.5) * 3.0
    capc = (np.array([150.0, 168.0, 182.0]) * (0.55 + 0.5 * nl)[..., None]) + (40 * nh ** 12)[..., None] + gr[..., None]
    in_cap = np.clip((SYNC_CAP - r) * AS, 0, 1)
    gap = np.clip(1 - np.abs(r - (SYNC_CAP + 0.3)) * AS / 1.2, 0, 1)            # joint sombre
    rgb = chrome * (1 - in_cap[..., None]) + capc * in_cap[..., None]
    rgb *= (1 - 0.75 * gap)[..., None]
    a = np.clip((rb1 - r) * AS, 0, 1)
    spr = PC._with_shadow(np.clip(rgb, 0, 255).astype(np.float32), a.astype(np.float32), 2 * SYNC_BEZ * AS, 0.5)
    # capuchon allume : bleu glace diffuse, coeur clair, texture depolie conservee
    core = np.exp(-(r / (SYNC_CAP * 0.78)) ** 2)
    lit = (np.array([150.0, 205.0, 255.0]) * (1 - 0.6 * core[..., None]) + np.array([245.0, 252.0, 255.0]) * 0.6 * core[..., None])
    lit = lit * (0.86 + 0.14 * nl)[..., None] + gr[..., None] + (30 * nh ** 12)[..., None]
    lit_a = in_cap * (1 - 0.7 * gap)
    on = np.dstack([np.clip(lit, 0, 255), lit_a * 255]).astype(np.float32)
    return spr, on, S_
SY_OFF, SY_ON, SY_S = sync_sprites()
over(img, SY_OFF, (SYNC[0] - SY_S / 2) * AS, (SYNC[1] - SY_S / 2) * AS)

# ------------------------------------------------------------------ 6. embases jack (photo du kit) : OUT a gauche, IN a droite (A et B)
print('jacks...')
alpha = body.copy()
for side in (-1, 1):
    j, jw_u, jh_u = PC.jack_sprite(JACK_LEN, AS, side)
    jh, jw = j.shape[:2]
    jw2 = int(math.floor(JACK_PROT * AS))
    if jw2 != jw:
        pm_ = j.copy(); pm_[..., :3] *= pm_[..., 3:4] / 255.0
        pm_ = cv2.resize(pm_, (jw2, jh), interpolation=cv2.INTER_AREA)
        a_ = np.maximum(pm_[..., 3:4], 1e-3); pm_[..., :3] = np.where(pm_[..., 3:4] > 0.5, pm_[..., :3] * 255.0 / a_, 0)
        j = pm_; jw = jw2
    for jy in JACK_YS:
        x0 = int(round((PX0 * AS - jw) if side < 0 else ((PX0 + PW) * AS)))
        y0 = int(round(jy * AS - jh / 2))
        occ = np.zeros((H, W), np.float32)
        occ[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
        contact = cv2.GaussianBlur(occ, (0, 0), 3.0 * AS)
        soft = cv2.GaussianBlur(occ, (0, 0), 16.0 * AS)
        o = np.clip(contact * 0.9 + soft * 1.5, 0, 0.55) * (0.25 if side > 0 else 0.6)
        img *= (1.0 - o * body)[..., None]
        over(img, j, x0, y0)
        alpha[y0:y0 + jh, x0:x0 + jw] = np.maximum(alpha[y0:y0 + jh, x0:x0 + jw], j[..., 3] / 255.0)
        del occ, contact, soft, o

# ------------------------------------------------------------------ 7. footswitch (sprite separe : dessine au-dessus du motif d'anneaux)
FSPR, FSREFL, FS_W, FS_BTN = PC.footswitch_sprite(FS_FLATS, AS, refl_colour=(255.0, 255.0, 255.0))
# occlusion douce du footswitch sur la facade (l'ombre portee est dans le sprite)
fa = np.zeros((H, W), np.float32); n_ = FSPR.shape[0]
for c in (FS_T, FS_B):
    x0, y0 = int(round((c[0] - FS_W / 2) * AS)), int(round((c[1] - FS_W / 2) * AS))
    fa[y0:y0 + n_, x0:x0 + n_] = np.maximum(fa[y0:y0 + n_, x0:x0 + n_], np.clip((FSPR[..., 3] / 255.0 - 0.86) / 0.14, 0, 1))
soft = cv2.GaussianBlur(fa, (0, 0), 14.0 * AS)
img *= (1.0 - np.clip(soft * 0.7, 0, 0.35) * (1 - fa) * body)[..., None]
del fa, soft

# ------------------------------------------------------------------ 8. sorties : recadrage 1235 x 1800
def to_out(a, ow=OUT_W, oh=OUT_H):
    x0, x1 = CROP_X0 * AS, (CROP_X0 + CROP_W) * AS
    y0, y1 = PY0 * AS, (PY0 + PH) * AS
    M = np.float32([[ow / (x1 - x0), 0, -x0 * ow / (x1 - x0)], [0, oh / (y1 - y0), -y0 * oh / (y1 - y0)]])
    return cv2.warpAffine(a, M, (ow, oh), flags=cv2.INTER_AREA)
print('sauvegarde...')
out_rgb = np.clip(to_out(img), 0, 255); out_a = np.clip(to_out(alpha), 0, 1)
Image.fromarray(np.dstack([out_rgb, out_a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'background.png'), optimize=True)

OUTS = 2.0 * SC                                  # pixels des sprites par unite de travail (= 2 px par unite du plugin)
def save_sprite(rgba, fn, units):
    n = int(round(units * OUTS))
    pm = rgba.astype(np.float32).copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    pm = cv2.resize(pm, (n, n), interpolation=cv2.INTER_AREA)
    a = np.clip(pm[..., 3:4], 1e-3, 255); pm[..., :3] = np.where(pm[..., 3:4] > 0.3, pm[..., :3] * 255.0 / a, 0)
    Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, fn), optimize=True)
save_sprite(FSPR, 'footswitch.png', FS_W)
save_sprite(FSREFL.astype(np.float32), 'fs_refl.png', FS_W)
for k, (on, S_) in LEDS.items(): save_sprite(on, k + '.png', S_)
save_sprite(SY_ON, 'sync_on.png', SY_S)

# ------------------------------------------------------------------ 9. facade eclairee par les LED (calques alpha : seule la lumiere ajoutee)
def glow(c, GR, col, ring, fn, h1=6.0, h2=22.0, gain=1.0):
    x0p, y0p = round((c[0] - GR) * AS), round((c[1] - GR) * AS)
    size = round(2 * GR * AS)
    reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
    E = gain * (1.1 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.176 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5)
    E *= np.clip((GR - d) / (0.27 * GR), 0, 1)
    E[d < ring] = 0.0
    col = np.array(col)
    lum = reg.mean(2, keepdims=True)
    lit = reg + (reg * 2.0 + 14.0 * np.clip(lum / 60.0, 0.3, 1.6)) * E[..., None] * col
    add = lit - reg
    a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
    rgba = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.float32)
    save_sprite(rgba, fn, 2 * GR)
    return (c[0] - GR, c[1] - GR, 2 * GR, 2 * GR)
print('lumieres...')
ICE, RED, GREEN, ORANGE = (0.55, 0.82, 1.0), (1.0, 0.2, 0.12), (0.25, 1.0, 0.35), (1.0, 0.55, 0.12)
GL = {}
GL['tempo'] = glow(LED_T, 100.0, ICE, LED_LENS * 1.07, 'glow_tempo.png')
for nm, col in (('red', RED), ('green', GREEN), ('orange', ORANGE)):
    GL['check_' + nm] = glow(LED_C, 100.0, col, LED_LENS * 1.07, 'glow_check_' + nm + '.png')
for i, y in enumerate(SLOTS):
    GL['slot%d' % i] = glow((SLOT_X, y), 46.0, ICE, SLOT_LENS * 1.07, 'glow_slot%d.png' % (i + 1), h1=4.0, h2=13.0, gain=0.8)
GL['sync'] = glow(SYNC, 80.0, ICE, SYNC_BEZ + 0.5, 'glow_sync.png', h1=9.0, h2=24.0, gain=0.55)
GL['x2'] = glow(X2, 70.0, ICE, 0.0, 'glow_x2.png', h1=10.0, h2=26.0, gain=0.35)

# ------------------------------------------------------------------ 10. serigraphie vectorielle (dessinee par le plugin) : textes, points, traits
VTEXT, VDOTS, VLINES, VTRI = [], [], [], []
def T(s, font, em, track, x, y, rot=0.0): VTEXT.append((s, font, em, track, x, y, rot))
for (pid, lab, x, y) in KNOBS:
    T(lab, 'medium', 17.0, 2.2, x, y + LABEL_DY)
    if pid != 'mode':
        for i in range(11):                               # graduations 0 a 10 sur 270 degres (course des potards)
            a = math.radians(-135 + 27 * i)
            rr = KNOB_R + 10.0
            VDOTS.append((x + rr * math.sin(a), y - rr * math.cos(a), 1.7))
# selecteur de mode : un trait par position (les noms des modes sont dessines par le plugin, mode choisi en surbrillance)
MODE_NAMES = ["LOOP", "ANALOG", "STANDARD", "TAPE", "WARM", "REVERSE", "+RV", "SHIM", "MOD", "WARP", "GLT"]
mx, my = KNOBS[4][2], KNOBS[4][3]
for i in range(11):
    a = math.radians(-135 + 27 * i)
    r0, r1 = KNOB_R + 4.0, KNOB_R + 10.0
    VLINES.append((mx + r0 * math.sin(a), my - r0 * math.cos(a), mx + r1 * math.sin(a), my - r1 * math.cos(a), 2.0))
MODE_LABEL_R = KNOB_R + 15.0
T('SYNC', 'medium', 17.0, 2.2, SYNC[0], KNOBS[4][3] + LABEL_DY)
for i, y in enumerate(SLOTS): T(str(i + 1), 'medium', 17.0, 0.0, SLOT_NUM_X, y)
T('EIGHT', 'bold', 36.0, 6.0, TITLE1[0], TITLE1[1])
T('ECHO', 'bold', 36.0, 6.0, TITLE2[0], TITLE2[1])
T('TAP', 'medium', 17.0, 2.2, FS_T[0], FS_LABEL_Y)
T('BYPASS', 'medium', 17.0, 2.2, FS_B[0], FS_LABEL_Y)
T('X2', 'bold', 34.0, 2.0, X2[0], X2[1])
for sgn in (-1, 1):                                       # traits de part et d'autre de X2
    VLINES.append((X2[0] + sgn * 30.0, X2[1], X2[0] + sgn * 50.0, X2[1], 2.6))
for nm, jy in zip(('A', 'B'), JACK_YS):
    T('OUT ' + nm, 'medium', 14.0, 1.6, PX0 + 21.0, jy, 90.0)
    T('IN ' + nm, 'medium', 14.0, 1.6, PX0 + PW - 21.0, jy, 90.0)
def tri(c, up, s=12.0):
    if up: VTRI.append((c[0] - s, c[1] + s * 0.42, c[0] + s, c[1] + s * 0.42, c[0], c[1] - s * 0.62))
    else:  VTRI.append((c[0] - s, c[1] - s * 0.42, c[0] + s, c[1] - s * 0.42, c[0], c[1] + s * 0.62))
tri(TRI_UP, True); tri(TRI_DN, False)
# zones reservees : le motif d'anneaux s'interrompt autour des inscriptions qu'il croise (comme une serigraphie)
from PIL import ImageFont
_FF = {k: os.path.join(ROOT, 'assets', 'fonts', v) for k, v in (('medium', 'Poppins-Medium.ttf'), ('bold', 'Poppins-Bold.ttf'), ('light', 'Poppins-Light.ttf'))}
def text_box(t, mx=6.0, my=4.0):
    s_, font, em, track, x, y, rot = t
    fnt = ImageFont.truetype(_FF[font], 200)
    w = (sum(fnt.getlength(ch) for ch in s_) / 200.0) * em + track * (len(s_) - 1)
    h = em * 0.74
    return (x - w / 2 - mx, y - h / 2 - my, w + 2 * mx, h + 2 * my)
GAPS = [text_box(t) for t in VTEXT if t[0] in ('TAP', 'BYPASS', 'ECHO')]
GAPS.append(text_box(('X2', 'bold', 34.0, 2.0, X2[0], X2[1], 0.0), mx=36.0, my=6.0))
for t in VTRI:
    xs, ys = t[0::2], t[1::2]
    GAPS.append((min(xs) - 7, min(ys) - 7, max(xs) - min(xs) + 14, max(ys) - min(ys) + 14))
_lh = LOGO_W * 244.0 / 2602.0
GAPS.append((LOGO_C[0] - LOGO_W / 2 - 8, LOGO_C[1] - _lh / 2 - 6, LOGO_W + 16, _lh + 12))
# motif d'anneaux (assets/eight_echo_motif.svg) : centres des groupes gauche / droit sur les footswitches
MOTIF_LEFT, MOTIF_RIGHT = (875.428571, 2048.0), (3220.571429, 2048.0)
MOTIF_K = (FS_B[0] - FS_T[0]) / (MOTIF_RIGHT[0] - MOTIF_LEFT[0])

# ------------------------------------------------------------------ 11. Layout.h + layout.json (repere du plugin 617,5 x 900)
def f(v): return f"{v:.2f}f"
def X(v): return (v - CROP_X0) * SC
def Y(v): return (v - PY0) * SC
def PT(p): return "{ %s, %s }" % (f(X(p[0])), f(Y(p[1])))
def RC(r): return "{ %s, %s, %s, %s }" % (f(X(r[0])), f(Y(r[1])), f(r[2] * SC), f(r[3] * SC))
fk = {'medium': 0, 'bold': 1, 'light': 2}
lay = {"frame": [OUT_W / 2, OUT_H / 2], "knobs": [[X(k[2]), Y(k[3]), KNOB_R * SC] for k in KNOBS],
       "slots": [[X(SLOT_X), Y(y)] for y in SLOTS], "sync": [X(SYNC[0]), Y(SYNC[1])],
       "ledTempo": [X(LED_T[0]), Y(LED_T[1])], "ledCheck": [X(LED_C[0]), Y(LED_C[1])],
       "fsTap": [X(FS_T[0]), Y(FS_T[1])], "fsBypass": [X(FS_B[0]), Y(FS_B[1])], "x2": [X(X2[0]), Y(X2[1])],
       "status": [X(STATUS[0]), Y(STATUS[1]), STATUS[2] * SC, STATUS[3] * SC], "jackYs": [Y(v) for v in JACK_YS],
       "jackL": X(PX0 - JACK_PROT / 2), "jackR": X(PX0 + PW + JACK_PROT / 2),
       "box": [X(PX0), Y(PY0), PW * SC, PH * SC]}
json.dump(lay, open(os.path.join(ROOT, 'tools', 'layout.json'), 'w'), indent=1)
with open(os.path.join(ROOT, 'Layout.h'), 'w') as fo:
    fo.write(f"// genere par tools/make_art.py - ne pas modifier a la main (repere {OUT_W / 2} x {OUT_H / 2} = fond {OUT_W} x {OUT_H} px / 2)\n#pragma once\n#include <juce_graphics/juce_graphics.h>\nnamespace layout\n{{\n")
    fo.write(f"    constexpr float frameW = {f(OUT_W / 2)}, frameH = {f(OUT_H / 2)};   // pedale plein cadre (jacks aux bords gauche / droit)\n")
    fo.write("    // ordre : elevel, mix, feedback, time, mode\n")
    fo.write("    const juce::Point<float> knobPos[5] = { " + ", ".join(PT(k[2:]) for k in KNOBS) + " };\n")
    fo.write(f"    const float knobR = {f(KNOB_R * SC)}, modeLabelR = {f(MODE_LABEL_R * SC)}, modeFont = {f(12.5 * SC)};\n")
    fo.write("    const juce::Point<float> slotPos[7] = { " + ", ".join(PT((SLOT_X, y)) for y in SLOTS) + " };\n")
    fo.write(f"    const float slotS = {f(LEDS['led_slot'][1] * SC)};\n")
    fo.write(f"    const juce::Point<float> ledTempo {PT(LED_T)}, ledCheck {PT(LED_C)}; const float ledS = {f(LEDS['led_ice'][1] * SC)};\n")
    fo.write(f"    const juce::Point<float> syncPos {PT(SYNC)}; const float syncR = {f(SYNC_BEZ * SC)}, syncS = {f(SY_S * SC)};\n")
    fo.write(f"    const juce::Point<float> fsTap {PT(FS_T)}, fsBypass {PT(FS_B)}; const float footR = {f(FS_BTN * SC)}, fsS = {f(FS_W * SC)};\n")
    fo.write(f"    const juce::Point<float> x2Pos {PT(X2)};\n")
    fo.write(f"    const juce::Point<float> triUp {PT(TRI_UP)}, triDown {PT(TRI_DN)};\n")
    for k, r in GL.items():
        fo.write(f"    const juce::Rectangle<float> glow_{k} {RC(r)};\n")
    fo.write(f"    const juce::Rectangle<float> statusRect {RC(STATUS)}; const float statusFont = {f(19.0 * SC)};\n")
    fo.write(f"    const juce::Rectangle<float> boxRect {RC((PX0, PY0, PW, PH))};   // boitier\n")
    fo.write("    // serigraphie vectorielle : texte, police (0 medium, 1 bold, 2 light), taille em, espacement, centre, rotation (degres)\n")
    fo.write("    struct Txt { const char* s; int font; float em, track, x, y, rot; };\n")
    fo.write("    const Txt texts[] = {\n" + ",\n".join(f'        {{ "{t[0]}", {fk[t[1]]}, {f(t[2] * SC)}, {f(t[3] * SC)}, {f(X(t[4]))}, {f(Y(t[5]))}, {f(t[6])} }}' for t in VTEXT) + "\n    };\n")
    fo.write("    struct Dot { float x, y, r; };\n")
    fo.write("    const Dot dots[] = { " + ", ".join(f"{{ {f(X(d[0]))}, {f(Y(d[1]))}, {f(d[2] * SC)} }}" for d in VDOTS) + " };\n")
    fo.write("    struct Line { float x0, y0, x1, y1, w; };\n")
    fo.write("    const Line lines[] = { " + ", ".join(f"{{ {f(X(l[0]))}, {f(Y(l[1]))}, {f(X(l[2]))}, {f(Y(l[3]))}, {f(l[4] * SC)} }}" for l in VLINES) + " };\n")
    fo.write("    struct Tri { float x0, y0, x1, y1, x2, y2; };\n")
    fo.write("    const Tri tris[] = { " + ", ".join("{ " + ", ".join(f(X(t[i])) if i % 2 == 0 else f(Y(t[i])) for i in range(6)) + " }" for t in VTRI) + " };\n")
    fo.write(f"    const float triStroke = {f(1.8 * SC)};\n")
    fo.write(f"    // motif d'anneaux (eight_echo_motif.svg, repere 4096) : point gauche du SVG -> footswitch TAP, echelle\n")
    fo.write(f"    const juce::Point<float> motifSvgLeft {{ {MOTIF_LEFT[0]:.3f}f, {MOTIF_LEFT[1]:.3f}f }}; const float motifScale = {MOTIF_K * SC:.6f}f;\n")
    fo.write(f"    const juce::Point<float> logoPos {PT(LOGO_C)}; const float logoW = {f(LOGO_W * SC)};\n")
    fo.write("    const juce::Rectangle<float> motifGaps[] = { " + ", ".join(RC(r) for r in GAPS) + " };\n")
    fo.write("}\n")

# ------------------------------------------------------------------ 12. donnees d'apercu (lues par tools/preview.py)
json.dump({"texts": [[t[0], t[1], t[2] * SC, t[3] * SC, X(t[4]), Y(t[5]), t[6]] for t in VTEXT],
           "dots": [[X(d[0]), Y(d[1]), d[2] * SC] for d in VDOTS],
           "lines": [[X(l[0]), Y(l[1]), X(l[2]), Y(l[3]), l[4] * SC] for l in VLINES],
           "tris": [[X(t[0]), Y(t[1]), X(t[2]), Y(t[3]), X(t[4]), Y(t[5])] for t in VTRI],
           "triStroke": 1.8 * SC, "motifLeft": MOTIF_LEFT, "motifScale": MOTIF_K * SC, "fsTap": [X(FS_T[0]), Y(FS_T[1])],
           "logo": [X(LOGO_C[0]), Y(LOGO_C[1]), LOGO_W * SC], "modeNames": MODE_NAMES, "modeLabelR": MODE_LABEL_R * SC,
           "modeFont": 12.5 * SC, "glows": {k: [X(r[0]), Y(r[1]), r[2] * SC, r[3] * SC] for k, r in GL.items()},
           "sprites": {"fs": FS_W * SC, "led": LEDS['led_ice'][1] * SC, "slot": LEDS['led_slot'][1] * SC, "sync": SY_S * SC},
           "knobR": KNOB_R * SC, "gaps": [[X(r[0]), Y(r[1]), r[2] * SC, r[3] * SC] for r in GAPS], "statusRect": [X(STATUS[0]), Y(STATUS[1]), STATUS[2] * SC, STATUS[3] * SC]},
          open(os.path.join(ROOT, 'tools', 'print.json'), 'w'), indent=0)
print('ok')
