"""
EIGHT ECHO (NINE HANDS | DSP) - visuel du plugin, entierement synthetise (v2.0, nov. 2026).

Regle NINE HANDS | DSP des pedales simples : image du plugin de 1235 x 1800 pixels, pedale plein cadre (le boitier touche
le haut et le bas de l'image, les jacks touchent les bords gauche et droit), fond transparent seulement autour des jacks.
Boitier : texture d'aluminium brosse fournie par l'utilisateur (assets/kit/brushed_texture.png, 4096 px) teintee du bleu gris
de la pedale d'origine, rendu en 4K (repere de travail 760 x 958 unites a 4 px par unite) puis ramene a 1235 x 1800.
Pieces photo du kit NINE HANDS | DSP (tools/photo_controls.py) : potards noirs en aluminium tourne, LED a lentille facettee
(tempo bleu glace, CHECK rouge / vert / orange), grosse LED du bouton SYNC (assets/kit/sync_led_photo.png),
footswitch d'Echoflex, embases jack (OUT a gauche, IN a droite). Memoires 1-7 : tubes de lumiere comme la pedale d'origine.
Une seule lumiere pour toute la pedale : en haut a gauche (ombres portees vers le bas a droite).

Textes (police de la pedale d'origine : Liberation Sans Bold, metrique Arial ; titre EIGHT ECHO et X2 dans le lettrage
d'origine reconstruit en traits vectoriels), graduations, traits, triangles, motif d'anneaux (assets/eight_echo_motif.svg)
et logo NINE HANDS | DSP (NineHandsLogo.svg) ne sont PAS imprimes dans le fond : le plugin les dessine en vectoriel (Layout.h).

Sorties (racine du depot) :
  background.png      fond 1235 x 1800 RGBA (boitier, potards sans repere, LED / tubes eteints, grosse LED SYNC eteinte, jacks)
  footswitch.png      footswitch (photo Echoflex) avec son ombre, dessine par le plugin PAR-DESSUS le motif d'anneaux
  fs_refl.png         reflet (blanc, canal alpha) de la LED voisine sur le flanc de l'ecrou, teinte par le plugin
  led_*.png, pipe_on.png, sync_on.png   elements allumes
  glow_*.png          facade eclairee par chaque lumiere (canal alpha = seule la lumiere ajoutee)
  Layout.h, tools/layout.json, tools/print.json (apercu)
Usage : python3 tools/make_art.py   (puis python3 tools/preview.py)
"""
import os, sys, math, json
import numpy as np, cv2
from PIL import Image, ImageFont

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
KD = (394.5 - 204.0) / 2 * KXo                   # potards symetriques par rapport au centre de la pedale
KL, KRX = CX - KD, CX + KD
KNOBS = [('elevel', 'E.LEVEL', KL, P(0, 149)[1]), ('mix', 'MIX', KRX, P(0, 149)[1]),
         ('feedback', 'FEEDBACK', KL, P(0, 311)[1]), ('time', 'TIME', KRX, P(0, 311)[1]), ('mode', 'MODE', KRX, P(0, 497)[1])]
LABEL_DY = 80.0                                  # etiquette sous le potard
SLOTS = [P(0, y)[1] for y in (94, 145, 197, 248, 300, 352, 403)]      # remontees, loin de OUT A (nov. 2026)
SLOT_NUM_X = PX0 + 70.0 * KXo                 # numeros decales avec les tubes allonges
FS_T, FS_B = (KL - 0.0, P(0, 775)[1]), (KRX, P(0, 775)[1])
FS_T = (CX - (438.0 - 143.0) / 2 * KXo, FS_T[1]); FS_B = (CX + (438.0 - 143.0) / 2 * KXo, FS_B[1])   # footswitches symetriques
SYNC = (KL, P(0, 491.5)[1]); SYNC_R = 29.0     # bouton lumineux SYNC (rayon exterieur de la bague)
LED_LENS = 11.0
LED_T = (FS_T[0], P(0, 621.0)[1]); LED_C = (FS_B[0], P(0, 621.0)[1])          # LED alignees sur les footswitches
TITLE_C = (CX, P(0, 637.5)[1])
TRI_UP, TRI_DN = (FS_T[0], P(0, 679)[1]), (FS_B[0], P(0, 677)[1])
FS_FLATS = 98.0
X2 = (CX, FS_T[1] + 2.0)
FS_LABEL_Y = P(0, 860)[1]
LOGO_C = (CX, P(0, 861)[1]); LOGO_W = 186.0
JACK_YS = [P(0, 480)[1], P(0, 622)[1]]           # A, B
STATUS = (CX - 150.0 * KXo, P(0, 30)[1], 300.0 * KXo, 40.0)   # zone de la ligne d'etat (cadre sombre, comme Screamer)
# tubes de lumiere des memoires (comme la pedale d'origine) : sortent de la tranche gauche en montant vers la droite
# mesures sur la pedale d'origine (ecartement des memoires = 52,3 px d'origine) : tube plat (incruste, sans relief),
# du bord interieur de l'arete (8 px) jusqu'au bout arrondi (42 px), monte a ~24 degres, 11 px d'epaisseur,
# acrylique a peine plus clair que la plaque avec un fin liseré clair sur le bord du bas ; centre = hauteur de la memoire
PIPE_R = 8.6 * KY                              # tubes elargis (demande nov. 2026)
PIPE_CUT = 8.0 * KXo                           # coupe droite cote arete
PIPE_A = (PIPE_CUT - 2.0, 7.0 * KY)            # depart (relatif : x depuis PX0, y depuis la memoire)
PIPE_B = (52.0 * KXo - PIPE_R, -8.5 * KY)      # centre du bout arrondi (tubes allonges vers la droite, nov. 2026)

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

# ------------------------------------------------------------------ 1. boitier : texture d'alu brosse fournie, teinte bleu gris, arete arrondie
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
# texture : 4096 px de cote, le boitier (PW x PH unites) la couvre sans repetition ; seul le relief (stries) est garde,
# la couleur vient de la teinte de la pedale d'origine
tex = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'kit', 'brushed_texture.png')).convert('L')).astype(np.float32)
bx0, by0, bw, bh = int(PX0 * AS), int(PY0 * AS), int(PW * AS), int(PH * AS)
tsc = max(bw / tex.shape[1], bh / tex.shape[0])
tex = cv2.resize(tex, (int(math.ceil(tex.shape[1] * tsc)), int(math.ceil(tex.shape[0] * tsc))), interpolation=cv2.INTER_CUBIC)
texf = np.full((H, W), float(tex.mean()), np.float32)
th_, tw_ = min(bh, tex.shape[0]), min(bw, tex.shape[1])
texf[by0:by0 + th_, bx0:bx0 + tw_] = tex[:th_, :tw_]
tex_rel = texf / float(tex.mean())               # ~1 +- 7 %
del tex, texf
paint = np.array([86.0, 103.0, 116.0], np.float32)            # bleu gris de la pedale d'origine
sheen = np.exp(-(((UY - (PY0 + 0.24 * PH)) / (0.30 * PH)) ** 2)) * (0.75 + 0.25 * np.exp(-((UX - (PX0 + 0.3 * PW)) / (0.7 * PW)) ** 2))
sheen = sheen.astype(np.float32)
spec_tint = np.array([0.92, 0.97, 1.0], np.float32)
contrast = 1.05                                                  # relief des stries un peu accentue (la texture est douce)
encl = paint * ((0.62 + 0.52 * ndl) * (1.0 + (tex_rel - 1.0) * contrast))[..., None]
encl += ((tex_rel - 1.0) * 40.0 * sheen)[..., None] * spec_tint          # les stries accrochent la lumiere dans le reflet
encl += (24.0 * sheen)[..., None] * spec_tint
encl += (70 * ndh ** 50 + 16 * ndh ** 6)[..., None] * spec_tint
del ndl, ndh, tex_rel
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
m_ = np.maximum(m_, np.clip((SYNC_R - np.hypot(UX - SYNC[0], UY - SYNC[1])) * AS, 0, 1) * 0.7)
occlusion(m_)
del m_

# ------------------------------------------------------------------ 3. potards (photo du kit, repere efface : seul le repere du plugin tourne)
for (_, _, x, y) in KNOBS:
    KN, KS = PC.knob_sprite(KNOB_R, AS)
    over(img, KN, (x - KS / 2) * AS, (y - KS / 2) * AS)

# ------------------------------------------------------------------ 4. LED tempo / CHECK eteintes (photo du kit) + lentilles allumees
LEDS = {}
def led(name, R, colour):
    off, on, S_ = PC.led_sprites(R, AS, colour=colour)
    LEDS[name] = (on, S_)
    return off, S_
off, S_ = led('led_ice', LED_LENS, 'ice'); over(img, off, (LED_T[0] - S_ / 2) * AS, (LED_T[1] - S_ / 2) * AS)
off, S_ = led('led_red', LED_LENS, 'red'); over(img, off, (LED_C[0] - S_ / 2) * AS, (LED_C[1] - S_ / 2) * AS)
led('led_green', LED_LENS, 'green'); led('led_orange', LED_LENS, 'orange')

# ------------------------------------------------------------------ 5. grosse LED du bouton SYNC (photo fournie : dome transparent)
SY_OFF, SY_ON, SY_S = PC.big_led_sprites(SYNC_R, AS)
over(img, SY_OFF, (SYNC[0] - SY_S / 2) * AS, (SYNC[1] - SY_S / 2) * AS)

# ------------------------------------------------------------------ 6. tubes de lumiere des memoires 1-7 (acrylique depoli)
print('tubes de lumiere...')
def seg_dist(px, py, a, b):
    ax, ay = a; bx, by = b
    vx, vy = bx - ax, by - ay
    t = np.clip(((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy), 0, 1)
    return np.hypot(px - (ax + t * vx), py - (ay + t * vy)), t
PIPE_BOX = (-8.0, -26.0, 74.0, 50.0)            # zone d'un tube (x0, y0 relatifs, largeur, hauteur)
def pipe_layers(ys):
    """renvoie (x0, y0 en unites, rgba eteint, rgba allume) d'un tube a la hauteur ys"""
    x0u, y0u = PX0 + PIPE_BOX[0], ys + PIPE_BOX[1]
    n_w, n_h = int(PIPE_BOX[2] * AS), int(PIPE_BOX[3] * AS)
    yy, xx = np.mgrid[0:n_h, 0:n_w].astype(np.float32)
    px, py = x0u + (xx + 0.5) / AS, y0u + (yy + 0.5) / AS
    A = (PX0 + PIPE_A[0], ys + PIPE_A[1]); B = (PX0 + PIPE_B[0], ys + PIPE_B[1])
    d, t = seg_dist(px, py, A, B)
    cov = np.clip((PIPE_R - d) * AS, 0, 1)
    # tranche gauche : le tube sort du boitier (coupe sur l'arete, comme sur la pedale d'origine)
    cov *= np.clip((px - (PX0 + PIPE_CUT)) * AS, 0, 1)
    # position dans la largeur du tube : -1 (bord du haut) .. +1 (bord du bas)
    ux, uy = (B[0] - A[0]), (B[1] - A[1]); ln = math.hypot(ux, uy); ux, uy = ux / ln, uy / ln
    nx_, ny_ = -uy, ux                                           # perpendiculaire vers le bas a droite
    sgn = np.sign((px - A[0]) * nx_ + (py - A[1]) * ny_)
    s = np.clip(d / PIPE_R, 0, 1) * sgn
    plate = img[int(y0u * AS):int(y0u * AS) + n_h, int(x0u * AS):int(x0u * AS) + n_w]
    # eteint : plat, incruste dans la plaque (aucun relief, aucune ombre) ; acrylique un peu plus clair que la plaque
    offc = plate * 0.80 + np.array([150.0, 160.0, 168.0]) * 0.20 + 30.0      # nettement plus clair que la plaque, sans volume
    lip = np.clip((s - 0.62) / 0.18, 0, 1) * np.clip((1.0 - s) / 0.12, 0, 1) * cov     # liseré clair, bord du bas
    offc = offc + (lip * 45.0)[..., None] * np.array([1.0, 1.02, 1.04])
    off_rgba = np.dstack([np.clip(offc, 0, 255), cov * 255]).astype(np.float32)
    # allume (comme l'original) : tube blanc lumineux, bord bleu glace, toujours plat
    # la lumiere deborde un peu du logement : forme allumee 1,6 unite plus large, bord adouci
    OVER = 1.6
    cov_l = np.clip((PIPE_R + OVER - d) / 1.2, 0, 1) * np.clip((px - (PX0 + PIPE_CUT)) * AS, 0, 1)
    sl = np.clip(d / (PIPE_R + OVER), 0, 1)
    core = np.clip(np.exp(-(sl / 0.80) ** 6) * (0.85 + 0.30 * t), 0, 1)
    lit = np.array([120.0, 190.0, 255.0]) * (1 - core[..., None]) + np.array([244.0, 250.0, 255.0]) * core[..., None]
    # halo lumineux autour du tube allume (bleu glace, s'eteint en douceur)
    halo = 0.75 * np.exp(-np.clip(d - PIPE_R, 0, None) / 6.0) * np.clip((px - (PX0 + PIPE_CUT - 2.0)) / 3.0, 0, 1)
    halo *= np.clip(1.0 - np.maximum(np.abs(px - (x0u + PIPE_BOX[2] / 2)) / (PIPE_BOX[2] / 2), np.abs(py - (y0u + PIPE_BOX[3] / 2)) / (PIPE_BOX[3] / 2)), 0, 1) ** 0.5
    a_on = np.clip(cov_l + halo * (1 - cov_l), 0, 1)
    halo_col = np.array([140.0, 205.0, 255.0])
    lit = np.where(cov_l[..., None] > 0, lit * cov_l[..., None] + halo_col * (1 - cov_l[..., None]), halo_col)
    lit = np.where(a_on[..., None] > 1e-3, lit, 0)
    on_rgba = np.dstack([np.clip(lit, 0, 255), a_on * 255]).astype(np.float32)
    return x0u, y0u, off_rgba, on_rgba
PIPES = []
for ys in SLOTS:
    x0u, y0u, off_rgba, on_rgba = pipe_layers(ys)
    a = off_rgba[..., 3] / 255.0
    over(img, off_rgba, x0u * AS, y0u * AS)
    PIPES.append((x0u, y0u, on_rgba))

# ------------------------------------------------------------------ 7. embases jack (photo du kit) : OUT a gauche, IN a droite (A et B)
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
        if side > 0:                                  # jacks de gauche : plus d'ombre sur la facade (demande nov. 2026)
            occ = np.zeros((H, W), np.float32)
            occ[y0:y0 + jh, x0:x0 + jw] = j[..., 3] / 255.0
            contact = cv2.GaussianBlur(occ, (0, 0), 3.0 * AS)
            soft = cv2.GaussianBlur(occ, (0, 0), 16.0 * AS)
            o = np.clip(contact * 0.9 + soft * 1.5, 0, 0.55) * 0.25
            img *= (1.0 - o * body)[..., None]
            del occ, contact, soft, o
        over(img, j, x0, y0)
        alpha[y0:y0 + jh, x0:x0 + jw] = np.maximum(alpha[y0:y0 + jh, x0:x0 + jw], j[..., 3] / 255.0)

# ------------------------------------------------------------------ 8. footswitch (sprite separe : dessine au-dessus du motif d'anneaux)
FSPR, FSREFL, FS_W, FS_BTN = PC.footswitch_sprite(FS_FLATS, AS, refl_colour=(255.0, 255.0, 255.0))
fa = np.zeros((H, W), np.float32); n_ = FSPR.shape[0]
for c in (FS_T, FS_B):
    x0, y0 = int(round((c[0] - FS_W / 2) * AS)), int(round((c[1] - FS_W / 2) * AS))
    fa[y0:y0 + n_, x0:x0 + n_] = np.maximum(fa[y0:y0 + n_, x0:x0 + n_], np.clip((FSPR[..., 3] / 255.0 - 0.86) / 0.14, 0, 1))
soft = cv2.GaussianBlur(fa, (0, 0), 14.0 * AS)
img *= (1.0 - np.clip(soft * 0.7, 0, 0.35) * (1 - fa) * body)[..., None]
del fa, soft

# ------------------------------------------------------------------ 9. sorties : recadrage 1235 x 1800
def to_out(a, ow=OUT_W, oh=OUT_H):
    x0, x1 = CROP_X0 * AS, (CROP_X0 + CROP_W) * AS
    y0, y1 = PY0 * AS, (PY0 + PH) * AS
    M = np.float32([[ow / (x1 - x0), 0, -x0 * ow / (x1 - x0)], [0, oh / (y1 - y0), -y0 * oh / (y1 - y0)]])
    return cv2.warpAffine(a, M, (ow, oh), flags=cv2.INTER_AREA)
print('sauvegarde...')
out_rgb = np.clip(to_out(img), 0, 255); out_a = np.clip(to_out(alpha), 0, 1)
Image.fromarray(np.dstack([out_rgb, out_a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'background.png'), optimize=True)

OUTS = 2.0 * SC                                  # pixels des sprites par unite de travail (= 2 px par unite du plugin)
def save_sprite(rgba, fn, units_w, units_h=None):
    nw = int(round(units_w * OUTS)); nh = int(round((units_h if units_h else units_w) * OUTS))
    pm = rgba.astype(np.float32).copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    pm = cv2.resize(pm, (nw, nh), interpolation=cv2.INTER_AREA)
    a = np.clip(pm[..., 3:4], 1e-3, 255); pm[..., :3] = np.where(pm[..., 3:4] > 0.3, pm[..., :3] * 255.0 / a, 0)
    Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, fn), optimize=True)
save_sprite(FSPR, 'footswitch.png', FS_W)
save_sprite(FSREFL.astype(np.float32), 'fs_refl.png', FS_W)
for k, (on, S_) in LEDS.items(): save_sprite(on, k + '.png', S_)
save_sprite(SY_ON, 'sync_on.png', SY_S)
save_sprite(PIPES[0][2], 'pipe_on.png', PIPE_BOX[2], PIPE_BOX[3])
for f_ in ('led_slot.png',):
    if os.path.exists(os.path.join(ROOT, f_)): os.remove(os.path.join(ROOT, f_))

# ------------------------------------------------------------------ 10. facade eclairee par les lumieres (calques alpha : seule la lumiere ajoutee)
def glow(sources, box, col, keep_out, fn, h1=6.0, h2=22.0, gain=1.0):
    """sources : liste de (x, y, poids) ; box : (x0, y0, w, h) en unites ; keep_out(px, py) -> masque (0 = pas de lumiere)"""
    x0u, y0u, wu, hu = box
    x0p, y0p = int(round(x0u * AS)), int(round(y0u * AS))
    nw, nh = int(round(wu * AS)), int(round(hu * AS))
    reg = img[y0p:y0p + nh, x0p:x0p + nw].astype(np.float64)
    yy, xx = np.mgrid[0:nh, 0:nw].astype(np.float64)
    px, py = x0u + (xx + 0.5) / AS, y0u + (yy + 0.5) / AS
    E = np.zeros((nh, nw))
    for (sx, sy, wgt) in sources:
        d2 = (px - sx) ** 2 + (py - sy) ** 2
        E += wgt * gain * (1.1 * h1 ** 3 / (d2 + h1 ** 2) ** 1.5 + 0.176 * h2 ** 3 / (d2 + h2 ** 2) ** 1.5)
    # retombee ronde et douce jusqu'aux bords de la zone (aucun bord de rectangle visible)
    ex = np.clip(np.minimum(px - x0u, x0u + wu - px) / (0.5 * wu), 0, 1)
    ey = np.clip(np.minimum(py - y0u, y0u + hu - py) / (0.5 * hu), 0, 1)
    fade = (np.sin(0.5 * np.pi * ex) * np.sin(0.5 * np.pi * ey)) ** 1.5
    E *= fade * cv2.GaussianBlur(keep_out(px, py), (0, 0), 0.8 * AS) * np.clip(alpha[y0p:y0p + nh, x0p:x0p + nw], 0, 1)
    col = np.array(col)
    # lumiere surtout additive et lisse (peu dependante des stries du brossage : plus de lueur rayee)
    base = cv2.GaussianBlur(reg, (0, 0), 3.0 * AS)
    lit = reg + (base * 0.9 + 0.35 * reg + 30.0) * E[..., None] * col
    add = lit - reg
    a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
    save_sprite(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.float32), fn, wu, hu)
    return box
def disc_out(c, r): return lambda px, py: (np.hypot(px - c[0], py - c[1]) > r).astype(np.float64)
print('lumieres...')
ICE, RED, GREEN, ORANGE = (0.55, 0.82, 1.0), (1.0, 0.2, 0.12), (0.25, 1.0, 0.35), (1.0, 0.55, 0.12)
GL = {}
def sq(c, r): return (c[0] - r, c[1] - r, 2 * r, 2 * r)
GL['tempo'] = glow([(LED_T[0], LED_T[1], 1.0)], sq(LED_T, 100.0), ICE, disc_out(LED_T, LED_LENS * 1.07), 'glow_tempo.png')
for nm, col in (('red', RED), ('green', GREEN), ('orange', ORANGE)):
    GL['check_' + nm] = glow([(LED_C[0], LED_C[1], 1.0)], sq(LED_C, 100.0), col, disc_out(LED_C, LED_LENS * 1.07), 'glow_check_' + nm + '.png')
for i, ys in enumerate(SLOTS):
    A = (PX0 + PIPE_CUT + 1.0, ys + PIPE_A[1]); B = (PX0 + PIPE_B[0], ys + PIPE_B[1])
    src = [(A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k, 0.12 + 0.20 * k) for k in np.linspace(0, 1, 8)]
    keep = (lambda A_, B_: (lambda px, py: ((seg_dist(px, py, A_, B_)[0] > PIPE_R) | (px < PX0 + PIPE_CUT)).astype(np.float64)))((PX0 + PIPE_A[0], ys + PIPE_A[1]), B)
    GL['slot%d' % i] = glow(src, (PX0 - 6.0, ys - 52.0, 130.0, 104.0), ICE, keep, 'glow_slot%d.png' % (i + 1), h1=5.5, h2=16.0, gain=2.6)
GL['sync'] = glow([(SYNC[0], SYNC[1], 1.0)], sq(SYNC, 82.0), ICE, disc_out(SYNC, SYNC_R * 0.97), 'glow_sync.png', h1=10.0, h2=26.0, gain=0.6)
PIPE_ON = [(x0u, y0u) for (x0u, y0u, _) in PIPES]

# ------------------------------------------------------------------ 11. lettrage d'origine (titre EIGHT ECHO, X2) en traits vectoriels
#     reconstruit d'apres le visuel d'origine (pixels de l'ancien visuel 578 x 896) : traits d'epaisseur constante,
#     angles arrondis, extremites droites ; le plugin les trace avec PathStrokeType (butt) et les remplit
def arc(cx, cy, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
LW = 6.5                                          # epaisseur du trait (pixels d'origine)
hw = LW / 2
def glyph(ch, x, top, h=30.5):
    y0, y1, ym = top + hw, top + h - hw, top + h / 2
    out = []
    if ch == 'E':
        w = 32.5; rc = 8.5; xl = x + hw
        out.append([(x + w, y0)] + arc(xl + rc, y0 + rc, rc, 270, 180) + arc(xl + rc, y1 - rc, rc, 180, 90) + [(x + w, y1)])
        out.append([(xl, ym), (x + w - 1.0, ym)])
    elif ch == 'I':
        out.append([(x + hw, top), (x + hw, top + h)]); w = LW
    elif ch == 'G':
        w = 36.0; rc = 13.0; xl = x + hw; xr = x + w - hw
        yb = top + 16.0                                               # barre interieure
        out.append([(x + w, y0)] + arc(xl + rc, y0 + rc, rc, 270, 180) + arc(xl + rc, y1 - rc, rc, 180, 90) + [(xr, y1), (xr, yb - hw)])
        out.append([(x + 18.0, yb), (x + w, yb)])
    elif ch == 'H':
        w = 34.5
        out.append([(x + hw, top), (x + hw, top + h)]); out.append([(x + w - hw, top), (x + w - hw, top + h)])
        out.append([(x + hw, top + 14.5), (x + w - hw, top + 14.5)])
    elif ch == 'T':
        w = 33.0
        out.append([(x, y0), (x + w, y0)]); out.append([(x + w / 2, y0), (x + w / 2, top + h)])
    elif ch == 'C':
        w = 35.0; rc = 13.0; xl = x + hw
        out.append([(x + w, y0)] + arc(xl + rc, y0 + rc, rc, 270, 180) + arc(xl + rc, y1 - rc, rc, 180, 90) + [(x + w, y1)])
    elif ch == 'O':
        w = 38.0; rc = 12.5; xl, xr = x + hw, x + w - hw
        pts = arc(xl + rc, y0 + rc, rc, 180, 270) + arc(xr - rc, y0 + rc, rc, 270, 360) + arc(xr - rc, y1 - rc, rc, 0, 90) + arc(xl + rc, y1 - rc, rc, 90, 180)
        out.append(pts + [pts[0], pts[1]])
    elif ch == 'X':
        w = 32.0
        out.append([(x + 1.5, top), (x + w - 1.5, top + h)]); out.append([(x + w - 1.5, top), (x + 1.5, top + h)])
    elif ch == '2':
        w = 31.0; rc = 7.0; xl, xr = x + hw, x + w - hw
        out.append([(x, y0)] + arc(xr - rc, y0 + rc, rc, 270, 360) + arc(xr - rc, ym - rc, rc, 0, 90) + arc(xl + rc, ym + rc, rc, 270, 180)
                   + [(xl, y1), (x + w, y1)])
    return out, w
def word(txt, x, top, gaps):
    strokes = []
    for ch, g in zip(txt, gaps):
        s, w = glyph(ch, x, top); strokes += s; x += w + g
    return strokes, x
# positions mesurees sur le visuel d'origine (bords gauches) : EIGHT 208 / 246 / 258 / 299.5 / 338.5, ECHO 213 / 249 / 289 / 328.5
tstrokes = []
for txt, xs, top in (('EIGHT', (208.0, 246.0, 258.0, 299.5, 338.5), 603.0), ('ECHO', (213.0, 249.0, 289.0, 328.5), 641.0)):
    for ch, x in zip(txt, xs):
        tstrokes += glyph(ch, x, top)[0]
x2strokes = glyph('X', 0.0, 0.0)[0] + glyph('2', 38.0, 0.0)[0]
TITLE_OLD_C = ((208.0 + 371.5) / 2, (603.0 + 672.0) / 2)
TK = KY                                           # meme echelle en x et y (lettrage non deforme)
def tmap(p, c_old, c_new, k=TK): return (c_new[0] + (p[0] - c_old[0]) * k, c_new[1] + (p[1] - c_old[1]) * k)
TITLE_STROKES = [[tmap(p, TITLE_OLD_C, TITLE_C) for p in s] for s in tstrokes]
X2K = TK * 1.12                                   # X2 agrandi (nov. 2026)
X2_STROKES = [[tmap(p, (34.5, 15.25), X2, X2K) for p in s] for s in x2strokes]
TITLE_W, X2_W = LW * TK, LW * X2K
# facade eclairee par X2 allume : source = traits du X2 (masque flou), calque alpha comme les LED
def x2_glow():
    GRx, GRy = 95.0, 45.0
    box = (X2[0] - GRx, X2[1] - GRy, 2 * GRx, 2 * GRy)
    nw, nh = int(box[2] * AS), int(box[3] * AS)
    m = np.zeros((nh, nw), np.uint8)
    for st in X2_STROKES + [[(X2[0] - X2_HALF - 9.0, X2[1]), (X2[0] - X2_HALF - 29.0, X2[1])], [(X2[0] + X2_HALF + 9.0, X2[1]), (X2[0] + X2_HALF + 29.0, X2[1])]]:
        pts = np.array([[(p[0] - box[0]) * AS * 4, (p[1] - box[1]) * AS * 4] for p in st], np.int32)
        cv2.polylines(m, [pts], False, 255, thickness=int(X2_W * AS), lineType=cv2.LINE_AA, shift=2)
    mk = m.astype(np.float64) / 255.0
    E = cv2.GaussianBlur(mk, (0, 0), 4.0 * AS) * 0.55 + cv2.GaussianBlur(mk, (0, 0), 14.0 * AS) * 0.45      # lueur reduite de 50 % (nov. 2026)
    x0p, y0p = int(round(box[0] * AS)), int(round(box[1] * AS))
    reg = img[y0p:y0p + nh, x0p:x0p + nw].astype(np.float64)
    yy, xx = np.mgrid[0:nh, 0:nw].astype(np.float64)
    fade = (np.sin(0.5 * np.pi * np.clip(np.minimum(xx, nw - xx) / (0.5 * nw), 0, 1)) * np.sin(0.5 * np.pi * np.clip(np.minimum(yy, nh - yy) / (0.5 * nh), 0, 1))) ** 1.5
    E *= fade
    col = np.array(ICE)
    base = cv2.GaussianBlur(reg, (0, 0), 3.0 * AS)
    add = (base * 0.9 + 0.35 * reg + 30.0) * E[..., None] * col
    a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
    save_sprite(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.float32), 'glow_x2.png', box[2], box[3])
    return box
# titre : logo EIGHT ECHO vectoriel fourni (assets/eight_echo_title.svg, contenu x 614,4-2385,9 / y 125,1-875,0),
# dessine par le plugin dans ce cadre (meme place et meme taille que le lettrage d'origine)
TITLE_SVG_BOUNDS = (614.42, 125.13, 2385.85 - 614.42, 875.0 - 125.13)
_th = 69.0 * TK; _tw = _th * TITLE_SVG_BOUNDS[2] / TITLE_SVG_BOUNDS[3]
TITLE_EXT = (TITLE_C[0] - _tw / 2, TITLE_C[1] - _th / 2, _tw, _th)

# ------------------------------------------------------------------ 12. serigraphie vectorielle (dessinee par le plugin) : textes, points, traits
VTEXT, VDOTS, VLINES, VTRI = [], [], [], []
def T(s, font, em, track, x, y, rot=0.0): VTEXT.append((s, font, em, track, x, y, rot))
LABEL_EM = 17.5
for (pid, lab, x, y) in KNOBS:
    T(lab, 'sans', LABEL_EM, 0.6, x, y + LABEL_DY)
    if pid != 'mode':
        for i in range(11):                               # graduations 0 a 10 sur 270 degres (course des potards)
            a = math.radians(-135 + 27 * i)
            rr = KNOB_R + 10.0
            VDOTS.append((x + rr * math.sin(a), y - rr * math.cos(a), 1.7))
MODE_NAMES = ["LOOP", "ANALOG", "STANDARD", "TAPE", "WARM", "REVERSE", "+RV", "SHIM", "MOD", "WARP", "GLT"]
mx, my = KNOBS[4][2], KNOBS[4][3]
for i in range(11):
    a = math.radians(-135 + 27 * i)
    r0, r1 = KNOB_R + 4.0, KNOB_R + 10.0
    VLINES.append((mx + r0 * math.sin(a), my - r0 * math.cos(a), mx + r1 * math.sin(a), my - r1 * math.cos(a), 2.0))
MODE_LABEL_R = KNOB_R + 15.0
T('SYNC', 'sans', LABEL_EM, 0.6, SYNC[0], KNOBS[4][3] + LABEL_DY)
for i, y in enumerate(SLOTS): T(str(i + 1), 'sans', 27.0 * KY, 0.0, SLOT_NUM_X, y - 19.0 * KY)
T('TAP', 'sans', LABEL_EM, 0.6, FS_T[0], FS_LABEL_Y)
T('BYPASS', 'sans', LABEL_EM, 0.6, FS_B[0], FS_LABEL_Y)
for nm, jy in zip(('A', 'B'), JACK_YS):
    T('OUT ' + nm, 'sans', 14.5, 0.8, PX0 + 21.0, jy, 90.0)
    T('IN ' + nm, 'sans', 14.5, 0.8, PX0 + PW - 21.0, jy, 90.0)
X2_HALF = 34.0 * X2K
GL['x2'] = x2_glow()
for sgn in (-1, 1):                                       # traits de part et d'autre de X2 (s'allument avec X2)
    VLINES.append((X2[0] + sgn * (X2_HALF + 9.0), X2[1], X2[0] + sgn * (X2_HALF + 29.0), X2[1], 2.6))
def tri(c, up, s=12.0):
    if up: VTRI.append((c[0] - s, c[1] + s * 0.42, c[0] + s, c[1] + s * 0.42, c[0], c[1] - s * 0.62))
    else:  VTRI.append((c[0] - s, c[1] - s * 0.42, c[0] + s, c[1] - s * 0.42, c[0], c[1] + s * 0.62))
tri(TRI_UP, True); tri(TRI_DN, False)
# zones reservees : le motif d'anneaux s'interrompt autour des inscriptions qu'il croise
FONT_FILES = {'sans': os.path.join(ROOT, 'assets', 'fonts', 'LiberationSans-Bold.ttf'),
              'mono': os.path.join(ROOT, 'assets', 'fonts', 'LiberationMono-Bold.ttf')}
def text_box(t, mx=6.0, my=4.0):
    s_, font, em, track, x, y, rot = t
    fnt = ImageFont.truetype(FONT_FILES[font], 200)
    w = (sum(fnt.getlength(ch) for ch in s_) / 200.0) * em + track * (len(s_) - 1)
    h = em * 0.72
    return (x - w / 2 - mx, y - h / 2 - my, w + 2 * mx, h + 2 * my)
GAPS = [text_box(t) for t in VTEXT if t[0] in ('TAP', 'BYPASS')]
GAPS.append((X2[0] - X2_HALF - 36.0, X2[1] - 15.25 * X2K - 7.0, 2 * X2_HALF + 72.0, 30.5 * X2K + 14.0))
GAPS.append((TITLE_EXT[0] - 6, TITLE_EXT[1] + TITLE_EXT[3] * 0.5, TITLE_EXT[2] + 12, TITLE_EXT[3] * 0.5 + 7))
for t in VTRI:
    xs, ys = t[0::2], t[1::2]
    GAPS.append((min(xs) - 7, min(ys) - 7, max(xs) - min(xs) + 14, max(ys) - min(ys) + 14))
_lh = LOGO_W * 244.0 / 2602.0
GAPS.append((LOGO_C[0] - LOGO_W / 2 - 8, LOGO_C[1] - _lh / 2 - 6, LOGO_W + 16, _lh + 12))
# motif d'anneaux (assets/eight_echo_motif.svg) : centres des groupes gauche / droit sur les footswitches
MOTIF_LEFT, MOTIF_RIGHT = (875.428571, 2048.0), (3220.571429, 2048.0)
MOTIF_K = (FS_B[0] - FS_T[0]) / (MOTIF_RIGHT[0] - MOTIF_LEFT[0])

# ------------------------------------------------------------------ 13. Layout.h + layout.json (repere du plugin 617,5 x 900)
def f(v): return f"{v:.2f}f"
def X(v): return (v - CROP_X0) * SC
def Y(v): return (v - PY0) * SC
def PT(p): return "{ %s, %s }" % (f(X(p[0])), f(Y(p[1])))
def RC(r): return "{ %s, %s, %s, %s }" % (f(X(r[0])), f(Y(r[1])), f(r[2] * SC), f(r[3] * SC))
fk = {'sans': 0, 'mono': 1}
SLOT_POS = [(PX0 + (PIPE_A[0] + PIPE_B[0]) / 2, y + (PIPE_A[1] + PIPE_B[1]) / 2) for y in SLOTS]
lay = {"frame": [OUT_W / 2, OUT_H / 2], "knobs": [[X(k[2]), Y(k[3]), KNOB_R * SC] for k in KNOBS],
       "slots": [[X(p[0]), Y(p[1])] for p in SLOT_POS], "sync": [X(SYNC[0]), Y(SYNC[1])],
       "ledTempo": [X(LED_T[0]), Y(LED_T[1])], "ledCheck": [X(LED_C[0]), Y(LED_C[1])],
       "fsTap": [X(FS_T[0]), Y(FS_T[1])], "fsBypass": [X(FS_B[0]), Y(FS_B[1])], "x2": [X(X2[0]), Y(X2[1])],
       "status": [X(STATUS[0]), Y(STATUS[1]), STATUS[2] * SC, STATUS[3] * SC], "jackYs": [Y(v) for v in JACK_YS],
       "jackL": X(PX0 - JACK_PROT / 2), "jackR": X(PX0 + PW + JACK_PROT / 2),
       "box": [X(PX0), Y(PY0), PW * SC, PH * SC], "title": [X(TITLE_EXT[0]), Y(TITLE_EXT[1]), TITLE_EXT[2] * SC, TITLE_EXT[3] * SC]}
json.dump(lay, open(os.path.join(ROOT, 'tools', 'layout.json'), 'w'), indent=1)
def strokes_c(name, strokes, w):
    pts, lens = [], []
    for s in strokes:
        lens.append(len(s)); pts += [f(X(p[0])) + ", " + f(Y(p[1])) for p in s]
    return (f"    const float {name}Pts[] = {{ " + ", ".join(pts) + " };\n"
            f"    const int {name}Lens[] = {{ " + ", ".join(str(n) for n in lens) + " };\n"
            f"    const float {name}Stroke = {f(w * SC)};\n")
with open(os.path.join(ROOT, 'Layout.h'), 'w') as fo:
    fo.write(f"// genere par tools/make_art.py - ne pas modifier a la main (repere {OUT_W / 2} x {OUT_H / 2} = fond {OUT_W} x {OUT_H} px / 2)\n#pragma once\n#include <juce_graphics/juce_graphics.h>\nnamespace layout\n{{\n")
    fo.write(f"    constexpr float frameW = {f(OUT_W / 2)}, frameH = {f(OUT_H / 2)};   // pedale plein cadre (jacks aux bords gauche / droit)\n")
    fo.write("    // ordre : elevel, mix, feedback, time, mode\n")
    fo.write("    const juce::Point<float> knobPos[5] = { " + ", ".join(PT(k[2:]) for k in KNOBS) + " };\n")
    fo.write(f"    const float knobR = {f(KNOB_R * SC)}, modeLabelR = {f(MODE_LABEL_R * SC)}, modeFont = {f(12.5 * SC)};\n")
    fo.write("    // tubes de lumiere des memoires 1-7 : centre (zone de clic), coin du sprite allume, calques de lumiere\n")
    fo.write("    const juce::Point<float> slotPos[7] = { " + ", ".join(PT(p) for p in SLOT_POS) + " };\n")
    fo.write("    const juce::Point<float> pipeOrigin[7] = { " + ", ".join(PT(p) for p in PIPE_ON) + " };\n")
    fo.write(f"    const float pipeW = {f(PIPE_BOX[2] * SC)}, pipeH = {f(PIPE_BOX[3] * SC)};\n")
    fo.write("    const juce::Rectangle<float> glowSlot[7] = { " + ", ".join(RC(GL['slot%d' % i]) for i in range(7)) + " };\n")
    fo.write(f"    const juce::Point<float> ledTempo {PT(LED_T)}, ledCheck {PT(LED_C)}; const float ledS = {f(LEDS['led_ice'][1] * SC)};\n")
    fo.write(f"    const juce::Point<float> syncPos {PT(SYNC)}; const float syncR = {f(SYNC_R * SC)}, syncS = {f(SY_S * SC)};\n")
    fo.write(f"    const juce::Point<float> fsTap {PT(FS_T)}, fsBypass {PT(FS_B)}; const float footR = {f(FS_BTN * SC)}, fsS = {f(FS_W * SC)};\n")
    fo.write(f"    const juce::Point<float> x2Pos {PT(X2)};\n")
    fo.write(f"    const juce::Point<float> triUp {PT(TRI_UP)}, triDown {PT(TRI_DN)};\n")
    for k in ('tempo', 'check_red', 'check_green', 'check_orange', 'sync', 'x2'):
        fo.write(f"    const juce::Rectangle<float> glow_{k} {RC(GL[k])};\n")
    fo.write(f"    const juce::Rectangle<float> statusRect {RC(STATUS)}; const float statusFont = {f(21.0 * SC)};\n")
    fo.write(f"    const juce::Rectangle<float> boxRect {RC((PX0, PY0, PW, PH))};   // boitier\n")
    fo.write("    // serigraphie vectorielle : texte, police (0 Liberation Sans Bold, 1 Liberation Mono Bold), taille em, espacement, centre, rotation (degres)\n")
    fo.write("    struct Txt { const char* s; int font; float em, track, x, y, rot; };\n")
    fo.write("    const Txt texts[] = {\n" + ",\n".join(f'        {{ "{t[0]}", {fk[t[1]]}, {f(t[2] * SC)}, {f(t[3] * SC)}, {f(X(t[4]))}, {f(Y(t[5]))}, {f(t[6])} }}' for t in VTEXT) + "\n    };\n")
    fo.write("    struct Dot { float x, y, r; };\n")
    fo.write("    const Dot dots[] = { " + ", ".join(f"{{ {f(X(d[0]))}, {f(Y(d[1]))}, {f(d[2] * SC)} }}" for d in VDOTS) + " };\n")
    fo.write("    struct Line { float x0, y0, x1, y1, w; };   // les 2 derniers : traits de X2 (allumes avec X2)\n")
    fo.write("    const Line lines[] = { " + ", ".join(f"{{ {f(X(l[0]))}, {f(Y(l[1]))}, {f(X(l[2]))}, {f(Y(l[3]))}, {f(l[4] * SC)} }}" for l in VLINES) + " };\n")
    fo.write("    struct Tri { float x0, y0, x1, y1, x2, y2; };\n")
    fo.write("    const Tri tris[] = { " + ", ".join("{ " + ", ".join(f(X(t[i])) if i % 2 == 0 else f(Y(t[i])) for i in range(6)) + " }" for t in VTRI) + " };\n")
    fo.write(f"    const float triStroke = {f(1.8 * SC)};\n")
    fo.write("    // lettrage d'origine (traits, extremites droites) : titre EIGHT ECHO et X2\n")
    fo.write(f"    const juce::Rectangle<float> titleRect {RC(TITLE_EXT)};   // logo EIGHT ECHO (eight_echo_title.svg)\n")
    fo.write(strokes_c('x2', X2_STROKES, X2_W))
    fo.write(f"    // motif d'anneaux (eight_echo_motif.svg, repere 4096) : point gauche du SVG -> footswitch TAP, echelle\n")
    fo.write(f"    const juce::Point<float> motifSvgLeft {{ {MOTIF_LEFT[0]:.3f}f, {MOTIF_LEFT[1]:.3f}f }}; const float motifScale = {MOTIF_K * SC:.6f}f;\n")
    fo.write(f"    const juce::Point<float> logoPos {PT(LOGO_C)}; const float logoW = {f(LOGO_W * SC)};\n")
    fo.write("    const juce::Rectangle<float> motifGaps[] = { " + ", ".join(RC(r) for r in GAPS) + " };\n")
    fo.write("}\n")

# ------------------------------------------------------------------ 14. donnees d'apercu (lues par tools/preview.py)
json.dump({"texts": [[t[0], t[1], t[2] * SC, t[3] * SC, X(t[4]), Y(t[5]), t[6]] for t in VTEXT],
           "dots": [[X(d[0]), Y(d[1]), d[2] * SC] for d in VDOTS],
           "lines": [[X(l[0]), Y(l[1]), X(l[2]), Y(l[3]), l[4] * SC] for l in VLINES],
           "tris": [[X(t[0]), Y(t[1]), X(t[2]), Y(t[3]), X(t[4]), Y(t[5])] for t in VTRI],
           "triStroke": 1.8 * SC, "motifLeft": MOTIF_LEFT, "motifScale": MOTIF_K * SC, "fsTap": [X(FS_T[0]), Y(FS_T[1])],
           "logo": [X(LOGO_C[0]), Y(LOGO_C[1]), LOGO_W * SC], "modeNames": MODE_NAMES, "modeLabelR": MODE_LABEL_R * SC,
           "modeFont": 12.5 * SC, "glows": {k: [X(r[0]), Y(r[1]), r[2] * SC, r[3] * SC] for k, r in GL.items()},
           "sprites": {"fs": FS_W * SC, "led": LEDS['led_ice'][1] * SC, "sync": SY_S * SC},
           "pipe": [[X(p[0]), Y(p[1])] for p in PIPE_ON], "pipeSize": [PIPE_BOX[2] * SC, PIPE_BOX[3] * SC],
           "titleRect": [X(TITLE_EXT[0]), Y(TITLE_EXT[1]), TITLE_EXT[2] * SC, TITLE_EXT[3] * SC], "titleSvgBounds": TITLE_SVG_BOUNDS,
           "x2": [[[X(p[0]), Y(p[1])] for p in s] for s in X2_STROKES], "x2W": X2_W * SC,
           "knobR": KNOB_R * SC, "gaps": [[X(r[0]), Y(r[1]), r[2] * SC, r[3] * SC] for r in GAPS],
           "statusRect": [X(STATUS[0]), Y(STATUS[1]), STATUS[2] * SC, STATUS[3] * SC]},
          open(os.path.join(ROOT, 'tools', 'print.json'), 'w'), indent=0)
print('ok')
