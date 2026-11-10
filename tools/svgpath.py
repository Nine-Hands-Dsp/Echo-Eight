"""petit lecteur de chemins SVG (M/L/H/V/C/S/A/Z), partage par make_art.py"""
import re, math
import numpy as np

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

