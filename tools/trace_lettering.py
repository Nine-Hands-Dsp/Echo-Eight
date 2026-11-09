"""
Vectorise le lettrage d'origine d'Eight Echo (titre EIGHT ECHO et X2 de l'ancien visuel, police de la pedale)
en contours : assets/lettering/lettering.json (polygones en pixels de l'ancien visuel 578 x 896).
Source : assets/lettering/old_background.png (visuel v1.x). A ne relancer que si la source change.
"""
import os, json
import numpy as np, cv2
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'lettering')
im = np.array(Image.open(os.path.join(SRC, 'old_background.png')).convert('RGBA')).astype(np.float32)
g = cv2.cvtColor(im[..., :3].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
x2 = np.array(Image.open(os.path.join(SRC, 'old_x2_on.png')).convert('RGBA')).astype(np.float32)
UP = 10

def trace(region, mask_extra=None, thr=150.0):
    x0, y0, x1, y1 = region
    sub = g[y0:y1, x0:x1].copy()
    if mask_extra is not None: sub = np.where(mask_extra, sub, 0)
    big = cv2.resize(sub, ((x1 - x0) * UP, (y1 - y0) * UP), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), 0.55 * UP)
    m = (big > thr).astype(np.uint8) * 255
    # bouche les petites encoches laissees par le biseau (jonction de la barre du H, etc.)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.6 * UP) | 1, int(1.6 * UP) | 1)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(0.8 * UP) | 1, int(0.8 * UP) | 1)))
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    polys = []
    for c in cs:
        if cv2.contourArea(c) < (4.0 * UP) ** 2: continue
        # lissage le long du contour puis simplification
        p = c[:, 0, :].astype(np.float32)
        n = len(p); k = max(3, UP // 2)
        pp = np.concatenate([p[-k:], p, p[:k]])
        ker = np.ones(2 * k + 1, np.float32) / (2 * k + 1)
        sm = np.stack([np.convolve(pp[:, 0], ker, 'valid'), np.convolve(pp[:, 1], ker, 'valid')], 1)
        ap = cv2.approxPolyDP(sm.reshape(-1, 1, 2), 0.22 * UP, True)[:, 0, :]
        polys.append([[float(x0 + (q[0] + 0.5) / UP - 0.5), float(y0 + (q[1] + 0.5) / UP - 0.5)] for q in ap])
    return polys

title = trace((195, 592, 385, 674))
# X2 : seulement les lettres (coeur du sprite allume de l'ancien visuel, place en 220, 727)
xa = x2[..., 3] / 255.0
X0, Y0 = 220, 727
mask = np.zeros(g.shape, bool)
core = cv2.dilate((xa > 0.6).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
mask[Y0:Y0 + xa.shape[0], X0:X0 + xa.shape[1]] = core
reg = (248, 755, 340, 800)
x2p = trace(reg, mask[reg[1]:reg[3], reg[0]:reg[2]], thr=140.0)
json.dump({'title': title, 'x2': x2p}, open(os.path.join(SRC, 'lettering.json'), 'w'))
print(len(title), 'contours titre ;', len(x2p), 'contours X2')
# controle visuel
c = np.zeros((900, 1900), np.uint8)
for p in title:
    q = np.array([[(x - 195) * 10, (y - 592) * 10] for x, y in p], np.int32); cv2.polylines(c, [q], True, 255, 2)
cv2.imwrite('/tmp/claude-0/trace_title.png', c)
