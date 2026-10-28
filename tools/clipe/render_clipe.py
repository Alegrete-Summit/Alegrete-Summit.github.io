#!/usr/bin/env python3
"""Clipe "IA + Inovação: a simbiose indissolúvel", do Alegrete Summit 2026.

Desenha cada quadro com Pillow (supersampling 2x e brilho por desfoque),
sintetiza a trilha com numpy e junta tudo com o ffmpeg.

Uso:
    python3 -I tools/clipe/render_clipe.py                 # vídeo completo
    python3 -I tools/clipe/render_clipe.py --stills 3 20   # só quadros PNG
    FFMPEG=/caminho/ffmpeg python3 -I tools/clipe/render_clipe.py
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", ".."))
FONTS = os.path.join(AQUI, "fonts")
FFMPEG_RESERVA = "/home/kreutz/.cache/uv/archive-v0/MNDvvea62LOz23Y7/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

W, H, FPS, DUR = 1280, 720, 30, 72.0
SS = 2  # supersampling da camada de geometria

GREEN = (25, 245, 140)
AMBER = (255, 181, 71)
WHITE = (245, 247, 245)
GRAY = (150, 162, 156)


# ---------------------------------------------------------------- utilidades

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def prog(t, a, b):
    return clamp((t - a) / (b - a))


def env(t, a, b, fi=0.7, fo=0.7):
    """Envelope de entrada e saída de uma cena ou legenda."""
    return ease(prog(t, a, a + fi)) * (1 - ease(prog(t, b - fo, b)))


def mix(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


def sc(c, a):
    a = clamp(a)
    return tuple(int(v * a) for v in c)


def lerp(p, q, k):
    return (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)


def partial(pts, k):
    """Primeira fração k (0..1) do comprimento de uma polilinha."""
    if k >= 1:
        return list(pts)
    if k <= 0:
        return [pts[0]]
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    d = sum(segs) * k
    out = [pts[0]]
    for i, s in enumerate(segs):
        if d >= s:
            out.append(pts[i + 1])
            d -= s
        else:
            out.append(lerp(pts[i], pts[i + 1], d / s if s else 0))
            break
    return out


_fc = {}
_FONT_FILES = {
    "russo": "RussoOne-Regular.ttf",
    "bold": "ChakraPetch-Bold.ttf",
    "semi": "ChakraPetch-SemiBold.ttf",
    "med": "ChakraPetch-Medium.ttf",
}


def font(name, size):
    k = (name, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(FONTS, _FONT_FILES[name]), int(size))
    return _fc[k]


# ------------------------------------------------------------------- quadro

class Frame:
    """Camada g (geometria 2x, com brilho) e camada t (texto nítido, sem brilho)."""

    def __init__(self):
        self.g = Image.new("RGB", (W * SS, H * SS))
        self.dg = ImageDraw.Draw(self.g)
        self.t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.dt = ImageDraw.Draw(self.t)

    def line(self, pts, c, w=2.0, a=1.0):
        if a <= 0.004 or len(pts) < 2:
            return
        self.dg.line([(x * SS, y * SS) for x, y in pts], fill=sc(c, a),
                     width=max(1, int(round(w * SS))), joint="curve")

    def dot(self, p, r, c, a=1.0, ring=0.0):
        if a <= 0.004:
            return
        x, y = p[0] * SS, p[1] * SS
        r *= SS
        box = [x - r, y - r, x + r, y + r]
        if ring:
            self.dg.ellipse(box, outline=sc(c, a), width=max(1, int(ring * SS)))
        else:
            self.dg.ellipse(box, fill=sc(c, a))

    def node(self, p, r, c, a=1.0, core=None):
        """Nó de circuito: anel com miolo."""
        self.dot(p, r, c, a, ring=max(1.5, r * 0.32))
        self.dot(p, r * 0.42, core or c, a)

    def ellipse(self, p, rx, ry, c, a=1.0, w=2.0):
        if a <= 0.004:
            return
        x, y = p[0] * SS, p[1] * SS
        self.dg.ellipse([x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS],
                        outline=sc(c, a), width=max(1, int(w * SS)))

    def gtext(self, xy, txt, f, size, c, a=1.0, anchor="mm"):
        """Texto na camada de geometria: ganha brilho."""
        if a <= 0.004:
            return
        self.dg.text((xy[0] * SS, xy[1] * SS), txt, font=font(f, size * SS),
                     fill=sc(c, a), anchor=anchor)

    def text(self, xy, txt, f, size, c, a=1.0, anchor="mm"):
        if a <= 0.004:
            return
        self.dt.text(xy, txt, font=font(f, size), fill=tuple(c) + (int(255 * clamp(a)),), anchor=anchor)

    def text_runs(self, cx, y, runs, f, size, a=1.0, glow=0.0, tracking=0):
        """Linha centrada com trechos de cores diferentes: [(texto, cor), ...]."""
        fnt = font(f, size)
        widths = []
        for s, _ in runs:
            widths.append(fnt.getlength(s) + tracking * len(s))
        x = cx - sum(widths) / 2
        for (s, c), wd in zip(runs, widths):
            if tracking:
                xx = x
                for ch in s:
                    self.text((xx, y), ch, f, size, c, a, anchor="lm")
                    if glow:
                        self.gtext((xx, y), ch, f, size, c, a * glow, anchor="lm")
                    xx += fnt.getlength(ch) + tracking
            else:
                self.text((x, y), s, f, size, c, a, anchor="lm")
                if glow:
                    self.gtext((x, y), s, f, size, c, a * glow, anchor="lm")
            x += wd

    def text_width(self, s, f, size):
        return font(f, size).getlength(s)

    def render(self):
        base = self.g.reduce(SS)
        arr = np.asarray(base, dtype=np.float32)
        g1 = base.reduce(2).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
        g2 = base.reduce(8).filter(ImageFilter.GaussianBlur(2.5)).resize((W, H), Image.BICUBIC)
        out = arr + 0.85 * np.asarray(g1, np.float32) + 1.6 * np.asarray(g2, np.float32)
        im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        im.alpha_composite(self.t)
        return im.convert("RGB")


# ---------------------------------------------------------- elementos fixos

def _circuit_paths():
    base = [
        [(0, 112), (64, 112), (124, 52), (318, 52)],
        [(0, 168), (34, 168), (34, 236)],
        [(150, 0), (150, 22), (206, 22)],
        [(0, 60), (22, 38), (22, 0)],
    ]
    paths = []
    for p in base:
        paths.append(p)
        paths.append([(W - x, y) for x, y in p])
        paths.append([(x, H - y) for x, y in p])
        paths.append([(W - x, H - y) for x, y in p])
    return paths


CIRCUITS = _circuit_paths()


def circuits(f, k, a):
    for i, p in enumerate(CIRCUITS):
        kk = ease(prog(k, (i % 4) * 0.08, 0.7 + (i % 4) * 0.08))
        if kk <= 0:
            continue
        pts = partial(p, kk)
        f.line(pts, GREEN, 1.6, a * 0.55)
        f.dot(p[0], 2.5, GREEN, a * 0.55)
        if kk >= 1:
            f.node(p[-1], 6, GREEN, a * 0.7)


def logo(f, cx, cy, size, k, a, c=GREEN):
    """Triângulo de três traços partidos com nós nas pontas."""
    A = (cx, cy - size * 0.56)
    B = (cx - size * 0.58, cy + size * 0.44)
    C = (cx + size * 0.58, cy + size * 0.44)
    strokes = [
        ([A, lerp(A, B, 0.6)], [1]),
        ([lerp(A, C, 0.3), C, lerp(C, B, 0.14)], [0, 2]),
        ([lerp(B, C, 0.02), (lerp(B, C, 0.5)[0], lerp(B, C, 0.5)[1] - size * 0.1)], [0, 1]),
    ]
    w = size * 0.075
    for i, (pts, nodes) in enumerate(strokes):
        kk = ease(prog(k, i * 0.25, i * 0.25 + 0.5))
        if kk <= 0:
            continue
        f.line(partial(pts, kk), c, w, a)
        f.dot(pts[0], w * 0.5, c, a)
        if kk >= 1:
            for n in nodes:
                f.dot(pts[n], size * 0.07, c, a)


# ------------------------------------------------------------------- cenas

T1, T2, T3, T4, T5, T6, T7, TEND = 0.0, 6.0, 14.5, 24.0, 40.0, 52.0, 62.0, DUR


def caption(f, t, a0, a1, txt, y=630, size=34, c=WHITE, runs=None):
    a = env(t, a0, a1, 0.45, 0.45)
    if a <= 0:
        return
    dy = (1 - eout(prog(t, a0, a0 + 0.6))) * 14
    if runs:
        f.text_runs(W / 2, y + dy, runs, "semi", size, a)
    else:
        f.text((W / 2, y + dy), txt, "semi", size, c, a)


def scene1(f, t):
    a = env(t, T1, T2, 0.3, 0.7)
    cx = W / 2
    logo(f, cx, 255, 175, prog(t, 0.8, 3.0), a)
    k = ease(prog(t, 2.4, 3.3))
    f.text_runs(cx, 420 + (1 - k) * 12, [("ALEGRETE", WHITE)], "russo", 70, a * k, tracking=4)
    k2 = ease(prog(t, 2.8, 3.7))
    f.text_runs(cx, 482, [("SUMMIT", WHITE)], "med", 34, a * k2, tracking=16)
    k3 = ease(prog(t, 3.2, 4.0))
    f.text_runs(cx, 532, [("2026", GREEN)], "bold", 30, a * k3, glow=0.5, tracking=10)
    k4 = ease(prog(t, 3.9, 4.6))
    f.text((cx, 612), "apresenta", "med", 24, GRAY, a * k4)


def ia_network(f, t, cx, cy, a, appear):
    counts = [3, 5, 5, 3]
    layers = []
    for l, n in enumerate(counts):
        x = cx + (l - 1.5) * 105
        layers.append([(x, cy + (j - (n - 1) / 2) * 62) for j in range(n)])
    edges = []
    for l in range(3):
        for p in layers[l]:
            for q in layers[l + 1]:
                edges.append((p, q))
    for i, (p, q) in enumerate(edges):
        kk = ease(prog(appear, 0.2 + (i % 7) * 0.05, 0.75 + (i % 7) * 0.05))
        f.line(partial([p, q], kk), GREEN, 1.1, a * 0.38)
    for l, ly in enumerate(layers):
        for j, p in enumerate(ly):
            kk = ease(prog(appear, l * 0.12, l * 0.12 + 0.35))
            f.node(p, 9, GREEN, a * kk, core=WHITE)
    if appear >= 0.8:
        pa = a * ease(prog(appear, 0.8, 1.0))
        for i, (p, q) in enumerate(edges):
            if i % 3:
                continue
            u = (t * 0.85 + i * 0.137) % 1.0
            f.dot(lerp(p, q, u), 3.2, mix(GREEN, WHITE, 0.6), pa)


def person(f, p, s, c, a):
    x, y = p
    f.dot((x, y - s * 0.55), s * 0.32, c, a)
    r = s * 0.6
    f.dg.arc([(x - r) * SS, (y + s * 0.1) * SS, (x + r) * SS, (y + s * 0.1 + 2 * r) * SS],
             180, 360, fill=sc(c, a), width=max(1, int(s * 0.16 * SS)))


def innovation_form(f, t, cx, cy, a, appear):
    R = 150 * eout(appear)
    if R < 2:
        return
    def blob(scale, ph):
        pts = []
        for i in range(121):
            th = 2 * math.pi * i / 120
            r = R * scale * (1 + 0.075 * math.sin(3 * th + t * 0.9 + ph) + 0.045 * math.sin(5 * th - t * 1.3))
            pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
        return pts
    f.line(blob(1.0, 0), AMBER, 2.6, a)
    f.line(blob(0.66, 1.7), AMBER, 1.4, a * 0.4)
    k = ease(prog(appear, 0.4, 1.0))
    for i, (dx, dy) in enumerate([(-48, -30), (8, -52), (52, 4), (-14, 34), (-62, 30)]):
        person(f, (cx + dx, cy + dy), 26, mix(AMBER, WHITE, 0.25), a * ease(prog(k, i * 0.12, i * 0.12 + 0.4)))
    for i in range(11):
        th = t * (0.35 + 0.05 * (i % 4)) + i * 2 * math.pi / 11
        rr = R * (1.18 + 0.06 * math.sin(t + i))
        f.dot((cx + rr * math.cos(th), cy + rr * math.sin(th)), 2.6 + (i % 3), AMBER, a * k * 0.9)


def scene2(f, t):
    a = env(t, T2, T3, 0.6, 0.6)
    if a <= 0:
        return
    merge = ease(prog(t, 13.4, 14.5))
    lx, rx, cy = 350 + merge * 130, 930 - merge * 130, 315
    ia_network(f, t, lx, cy, a, prog(t, 6.2, 8.2))
    innovation_form(f, t, rx, cy, a, prog(t, 6.6, 8.6))
    k = ease(prog(t, 7.3, 8.0)) * (1 - merge)
    f.text((lx, 512), "IA", "bold", 34, GREEN, a * k)
    f.text((lx, 548), "dados · modelos · algoritmos", "med", 19, GRAY, a * k)
    f.text((rx, 512), "INOVAÇÃO", "bold", 34, AMBER, a * k)
    f.text((rx, 548), "pessoas · ideias · território", "med", 19, GRAY, a * k)
    caption(f, t, 8.2, 11.2, None, runs=[("IA", GREEN), (" sem inovação perde o ", WHITE), ("sentido", AMBER), (".", WHITE)])
    caption(f, t, 11.2, 14.3, None, runs=[("Inovação", AMBER), (" sem IA perde a ", WHITE), ("velocidade", GREEN), (".", WHITE)])


def scene3(f, t):
    a = env(t, T3 - 0.2, T4, 0.8, 0.7)
    if a <= 0:
        return
    cy, A, lam = 372, 74, 330
    half = 560 * eout(prog(t, 14.4, 16.6))
    ph = t * 1.5
    x0, x1 = W / 2 - half, W / 2 + half
    xs = np.arange(x0, x1 + 0.1, 7.0)
    th = 2 * math.pi * (xs - W / 2) / lam + ph
    s, c = np.sin(th), np.cos(th)
    y1, y2 = cy + A * s, cy - A * s
    edge = np.clip(np.minimum(xs - x0, x1 - xs) / 60.0, 0, 1)
    for i in range(len(xs) - 1):
        d1 = (1 + c[i]) / 2
        d2 = 1 - d1
        f.line([(xs[i], y1[i]), (xs[i + 1], y1[i + 1])], GREEN, 1.6 + 2.6 * d1, a * edge[i] * (0.35 + 0.65 * d1))
        f.line([(xs[i], y2[i]), (xs[i + 1], y2[i + 1])], AMBER, 1.6 + 2.6 * d2, a * edge[i] * (0.35 + 0.65 * d2))
    # degraus: do verde ao âmbar
    step = 4
    for i in range(0, len(xs), step):
        if abs(s[i]) < 0.12:
            continue
        aa = a * edge[i] * 0.75
        for j in range(6):
            p = (xs[i], y1[i] + (y2[i] - y1[i]) * j / 6)
            q = (xs[i], y1[i] + (y2[i] - y1[i]) * (j + 1) / 6)
            f.line([p, q], mix(GREEN, AMBER, (j + 0.5) / 6), 1.4, aa * 0.7)
        d1 = (1 + c[i]) / 2
        f.dot((xs[i], y1[i]), 3 + 2.5 * d1, GREEN, aa * (0.5 + 0.5 * d1))
        f.dot((xs[i], y2[i]), 3 + 2.5 * (1 - d1), AMBER, aa * (0.5 + 0.5 * (1 - d1)))
    k = ease(prog(t, 15.6, 16.6))
    f.text_runs(W / 2, 150 - (1 - k) * 14, [("IA", GREEN), (" + ", WHITE), ("INOVAÇÃO", AMBER)], "russo", 74, a * k, glow=0.35)
    k2 = ease(prog(t, 17.0, 17.8))
    f.text((W / 2, 572), "a simbiose indissolúvel", "semi", 38, WHITE, a * k2)
    k3 = ease(prog(t, 19.2, 20.0))
    f.text((W / 2, 622), "uma não avança sem a outra", "med", 24, GRAY, a * k3)


SECTORS = ["Arroz e água", "Pecuária", "Energia", "Saúde", "Educação",
           "Gestão pública", "Comércio e serviços", "Logística de fronteira"]


def horizon_y(x):
    return 470 - 10 * math.sin(x / 170 + 0.6) - 5 * math.sin(x / 61)


def scene4(f, t):
    a = env(t, T4, T5, 0.8, 0.7)
    if a <= 0:
        return
    g = ease(prog(t, 24.0, 25.6))
    # sol baixo
    sy = 470 + 26 * (1 - ease(prog(t, 24.0, 30.0)))
    r = 62
    f.dg.pieslice([(1000 - r) * SS, (sy - r) * SS, (1000 + r) * SS, (sy + r) * SS], 180, 360, fill=sc(AMBER, a * g * 0.85))
    f.dg.rectangle([0, 470 * SS, W * SS, 480 * SS + 1], fill=(0, 0, 0))
    # horizonte de coxilhas
    hx = np.arange(0, W + 1, 8)
    pts = [(x, horizon_y(x)) for x in hx]
    f.dg.polygon([(x * SS, y * SS) for x, y in pts] + [(W * SS, H * SS), (0, H * SS)], fill=(0, 0, 0))
    f.line(partial(pts, g), GREEN, 2.2, a)
    # lavouras de arroz: linhas em perspectiva e taipas
    gk = ease(prog(t, 24.6, 26.4))
    vp = (640, 474)
    for i, xb in enumerate(range(-700, 1981, 150)):
        f.line(partial([vp, (xb, H + 10)], gk), GREEN, 1.0, a * 0.16)
    for k in range(1, 6):
        y = 474 + 250 * (k / 5) ** 1.7
        tp = [(x, y + 4 * math.sin(x / 90 + k)) for x in range(0, W + 1, 16)]
        f.line(partial(tp, gk), GREEN, 1.2, a * 0.22)
    # umbu solitário
    tx = 78
    ty = horizon_y(tx)
    f.line([(tx, ty), (tx - 3, ty - 34)], GREEN, 3.2, a * gk * 0.85)
    f.line([(tx - 3, ty - 26), (tx - 20, ty - 42)], GREEN, 2.0, a * gk * 0.85)
    f.line([(tx - 2, ty - 30), (tx + 16, ty - 46)], GREEN, 2.0, a * gk * 0.85)
    f.ellipse((tx - 2, ty - 58), 50, 24, GREEN, a * gk * 0.85, 2.2)
    # setores
    nodes = []
    for i in range(8):
        x = 125 + i * 147
        y = 250 if i % 2 == 0 else 345
        nodes.append((x, y))
    times = [25.4 + i * 1.2 for i in range(8)]
    for i in range(8):
        on = ease(prog(t, times[i], times[i] + 0.5))
        if i > 0:
            ek = ease(prog(t, times[i] - 0.65, times[i]))
            f.line(partial([nodes[i - 1], nodes[i]], ek), mix(GREEN, AMBER, 0.15), 2.0, a * 0.8)
        if i > 1:
            ek = ease(prog(t, times[i] - 0.4, times[i] + 0.4))
            f.line(partial([nodes[i - 2], nodes[i]], ek), GREEN, 1.0, a * 0.3)
        if on <= 0:
            continue
        x, y = nodes[i]
        hy = horizon_y(x)
        for yy in np.arange(y + 14, hy - 4, 12):
            f.line([(x, yy), (x, min(yy + 5, hy - 4))], GREEN, 1.0, a * on * 0.35)
        pulse = 1 + 0.35 * math.exp(-4 * max(0.0, t - times[i]))
        f.node((x, y), 11 * pulse, GREEN, a * on, core=AMBER)
        label = SECTORS[i]
        wdt = f.text_width(label, "semi", 22)
        lx = clamp(x, 22 + wdt / 2, W - 22 - wdt / 2)
        ly = y - 32 if i % 2 == 0 else y + 34
        f.text((lx, ly), label, "semi", 22, WHITE, a * on)
    if t > times[-1] + 0.4:
        pa = a * ease(prog(t, times[-1] + 0.4, times[-1] + 1.2))
        for i in range(1, 8):
            u = (t * 0.7 + i * 0.31) % 1.0
            f.dot(lerp(nodes[i - 1], nodes[i], u), 3.4, mix(AMBER, WHITE, 0.5), pa)
    caption(f, t, 24.6, 40.2, None, y=104, size=38,
            runs=[("Cada setor do ", WHITE), ("Pampa", AMBER), (", uma nova ", WHITE), ("conexão", GREEN), (".", WHITE)])
    k = ease(prog(t, 35.4, 36.2))
    f.text((W / 2, 150), "IA a serviço de quem produz, cuida, ensina, governa e empreende.", "med", 22, GRAY, a * k)


LOOP = [("Dados", GREEN), ("Modelos", GREEN), ("Decisões", mix(GREEN, AMBER, 0.5)),
        ("Pessoas", AMBER), ("Novos problemas", AMBER)]


def scene5(f, t):
    a = env(t, T5, T6, 0.8, 0.7)
    if a <= 0:
        return
    cx, cy, R = 420, 372, 168
    n = len(LOOP)
    ang = [-math.pi / 2 + i * 2 * math.pi / n for i in range(n)]
    pos = [(cx + R * math.cos(q), cy + R * math.sin(q)) for q in ang]
    base = 40.4
    for i in range(n):
        on = ease(prog(t, base + i * 0.7, base + i * 0.7 + 0.5))
        # arco até o próximo nó
        q0 = ang[i] + 0.2
        q1 = ang[i] + 2 * math.pi / n - 0.2
        ek = ease(prog(t, base + i * 0.7 + 0.3, base + i * 0.7 + 0.9))
        if ek > 0:
            qs = np.linspace(q0, q0 + (q1 - q0) * ek, 30)
            c0, c1 = LOOP[i][1], LOOP[(i + 1) % n][1]
            arc = [(cx + R * math.cos(q), cy + R * math.sin(q)) for q in qs]
            for j in range(len(arc) - 1):
                f.line([arc[j], arc[j + 1]], mix(c0, c1, j / len(arc)), 2.2, a * 0.85)
            if ek >= 1:
                tip = arc[-1]
                q = q1
                tx, ty = -math.sin(q), math.cos(q)  # tangente
                nx, ny = math.cos(q), math.sin(q)
                b = (tip[0] - tx * 13, tip[1] - ty * 13)
                f.dg.polygon([(tip[0] * SS, tip[1] * SS),
                              ((b[0] + nx * 7) * SS, (b[1] + ny * 7) * SS),
                              ((b[0] - nx * 7) * SS, (b[1] - ny * 7) * SS)], fill=sc(c1, a))
        if on <= 0:
            continue
        name, col = LOOP[i]
        f.node(pos[i], 13, col, a * on, core=WHITE)
        d = (math.cos(ang[i]), math.sin(ang[i]))
        lp = (cx + (R + 34) * d[0], cy + (R + 34) * d[1])
        anchor = "lm" if d[0] > 0.3 else "rm" if d[0] < -0.3 else "mm"
        if anchor == "mm":
            lp = (lp[0], lp[1] + (6 if d[1] > 0 else -4))
        f.text(lp, name, "semi", 24, WHITE, a * on, anchor=anchor)
    k = ease(prog(t, 43.6, 44.4))
    f.text((cx, cy - 14), "IA", "bold", 30, GREEN, a * k)
    f.text((cx, cy + 20), "+ pessoas", "semi", 22, AMBER, a * k)
    if t > 44.0:
        pa = a * ease(prog(t, 44.0, 44.6))
        q = -math.pi / 2 + ((t - 44.0) / 2.6) * 2 * math.pi
        u = ((q + math.pi / 2) % (2 * math.pi)) / (2 * math.pi)
        col = mix(GREEN, AMBER, clamp(u * 1.6 - 0.2))
        for k2 in range(6):
            qq = q - k2 * 0.05
            f.dot((cx + R * math.cos(qq), cy + R * math.sin(qq)), 5.5 - k2 * 0.7, mix(col, WHITE, 0.4), pa * (1 - k2 / 6))
    f.text((W / 2, 70), "o ciclo da inovação com IA", "med", 22, GRAY, a * ease(prog(t, 40.6, 41.4)))
    rows = [
        (42.6, [("A IA aprende com ", WHITE), ("dados", GREEN), (".", WHITE)]),
        (45.2, [("A inovação aprende com ", WHITE), ("pessoas", AMBER), (".", WHITE)]),
        (47.8, [("Supervisão humana", AMBER), (" em cada volta.", WHITE)]),
    ]
    for i, (t0, runs) in enumerate(rows):
        k = ease(prog(t, t0, t0 + 0.6))
        if k <= 0:
            continue
        y = 282 + i * 82
        x = 772 + (1 - eout(prog(t, t0, t0 + 0.7))) * 24
        fnt = font("semi", 29)
        for s, c in runs:
            f.text((x, y), s, "semi", 29, c, a * k, anchor="lm")
            x += fnt.getlength(s)
        f.line([(752, y - 16), (752, y + 16)], runs[-2][1] if len(runs) > 2 else runs[0][1], 3, a * k)


HELICES = ["Poder público", "Empresas", "Academia", "Sociedade"]


def scene6(f, t):
    a = env(t, T6, T7, 0.8, 0.7)
    if a <= 0:
        return
    deck = 468
    xL, xR = 110, 1170
    piers = [210, 503, 777, 1070]
    for i, x in enumerate(piers):
        k = ease(prog(t, 52.4 + i * 0.45, 53.3 + i * 0.45))
        if k <= 0:
            continue
        f.line([(x, 600), (x, 600 - (600 - deck) * k)], AMBER, 4, a)
        f.dg.rectangle([(x - 26) * SS, 600 * SS, (x + 26) * SS, 604 * SS], fill=sc(AMBER, a * k))
        f.text((x, 636), HELICES[i], "semi", 25, WHITE, a * k)
    dk = ease(prog(t, 54.0, 55.4))
    if dk > 0:
        mid = (xL + xR) / 2
        f.line([(mid - (mid - xL) * dk, deck), (mid + (xR - mid) * dk, deck)], AMBER, 3.4, a)
    def arch_y(x):
        return deck - 228 * math.sin(math.pi * (x - xL) / (xR - xL))
    ak = ease(prog(t, 55.0, 57.4))
    if ak > 0:
        xsL = np.linspace(xL, xL + (xR - xL) / 2 * ak, 60)
        xsR = np.linspace(xR, xR - (xR - xL) / 2 * ak, 60)
        f.line([(x, arch_y(x)) for x in xsL], GREEN, 3.2, a)
        f.line([(x, arch_y(x)) for x in xsR], GREEN, 3.2, a)
        nx = np.linspace(xL, xR, 15)
        for x in nx:
            if abs(x - (xL + xR) / 2) <= (xR - xL) / 2 * ak + 1:
                f.dot((x, arch_y(x)), 5, GREEN, a)
    hk = prog(t, 56.8, 58.6)
    if hk > 0:
        hx = np.linspace(xL + 35, xR - 35, 26)
        for i, x in enumerate(hx):
            kk = ease(prog(hk, i / 26 * 0.6, i / 26 * 0.6 + 0.4))
            if kk <= 0:
                continue
            y0 = arch_y(x)
            y1 = y0 + (deck - y0) * kk
            segs = 5
            for j in range(segs):
                p = (x, y0 + (y1 - y0) * j / segs)
                q = (x, y0 + (y1 - y0) * (j + 1) / segs)
                f.line([p, q], mix(GREEN, AMBER, (j + 0.5) / segs * kk), 1.3, a * 0.75)
    if t > 58.4:
        pa = a * ease(prog(t, 58.4, 59.0))
        for i in range(3):
            u = ((t - 58.4) * 0.28 + i / 3) % 1.0
            x = xL + (xR - xL) * u
            f.dot((x, arch_y(x)), 5, mix(GREEN, WHITE, 0.5), pa)
            x2 = xR - (xR - xL) * u
            f.dot((x2, deck), 5, mix(AMBER, WHITE, 0.5), pa)
    k1 = ease(prog(t, 56.2, 57.0))
    f.text((W / 2, 96 - (1 - k1) * 12), "Inovar é construir pontes.", "semi", 40, WHITE, a * k1)
    k2 = ease(prog(t, 58.0, 58.8))
    f.text_runs(W / 2, 150 - (1 - k2) * 12, [("A ", WHITE), ("IA", GREEN), (" é a nova ponte.", WHITE)], "semi", 40, a * k2)


def scene7(f, t):
    a = ease(prog(t, T7, T7 + 0.8)) * (1 - ease(prog(t, 70.4, 71.8)))
    if a <= 0:
        return
    logo(f, W / 2, 192, 132, prog(t, 62.2, 63.8), a)
    k1 = ease(prog(t, 63.4, 64.2))
    f.text_runs(W / 2, 352 - (1 - k1) * 12, [("IA", GREEN), (" + ", WHITE), ("INOVAÇÃO", AMBER)], "russo", 64, a * k1, glow=0.35)
    k2 = ease(prog(t, 64.2, 65.0))
    f.text((W / 2, 420), "simbiose indissolúvel e necessária", "semi", 34, WHITE, a * k2)
    k3 = ease(prog(t, 65.4, 66.2))
    f.line([(W / 2 - 260 * k3, 474), (W / 2 + 260 * k3, 474)], GREEN, 1.6, a * k3)
    f.dot((W / 2 - 260 * k3, 474), 4, GREEN, a * k3)
    f.dot((W / 2 + 260 * k3, 474), 4, GREEN, a * k3)
    f.text_runs(W / 2, 516, [("ALEGRETE SUMMIT 2026", WHITE)], "bold", 26, a * k3, tracking=3)
    k4 = ease(prog(t, 66.0, 66.8))
    f.text((W / 2, 560), "29 e 30 de outubro de 2026  ·  Sicredi Essência  ·  Alegrete/RS", "med", 23, GRAY, a * k4)
    k5 = ease(prog(t, 66.8, 67.6))
    f.text_runs(W / 2, 606, [("Inovar é ", WHITE), ("construir pontes", GREEN), (".", WHITE)], "semi", 24, a * k5)


def draw(t):
    f = Frame()
    fade_out = 1 - ease(prog(t, 70.6, 71.9))
    circuits(f, prog(t, 0.0, 2.6), (0.55 if T4 < t < T5 else 1.0) * fade_out)
    for sc_fn, a, b in [(scene1, T1, T2 + 0.1), (scene2, T2 - 0.1, T3 + 0.1), (scene3, T3 - 0.3, T4 + 0.1),
                        (scene4, T4 - 0.1, T5 + 0.1), (scene5, T5 - 0.1, T6 + 0.1),
                        (scene6, T6 - 0.1, T7 + 0.1), (scene7, T7 - 0.1, TEND)]:
        if a <= t <= b:
            sc_fn(f, t)
    return f.render()


# -------------------------------------------------------------------- trilha

def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def intensity(t):
    keys = [(0, 0.05), (6, 0.18), (13.5, 0.38), (15.5, 0.85), (23.5, 0.62), (39.5, 0.55),
            (51.5, 0.6), (54.5, 0.98), (61.5, 0.92), (66, 0.4), (72, 0.0)]
    xs, ys = zip(*keys)
    return np.interp(t, xs, ys)


def soundtrack(path, sr=48000):
    n = int(DUR * sr)
    tt = np.arange(n) / sr
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(7)
    seg = 4.8  # dois compassos a 100 bpm
    chords = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [48, 55, 60, 64, 67], [52, 55, 59, 62, 67]]
    roots = [33, 29, 36, 28]
    nseg = int(math.ceil(DUR / seg))
    # pad
    for s in range(nseg):
        ch = chords[s % 4]
        t0 = s * seg
        i0 = int(max(0, t0 - 1.0) * sr)
        i1 = min(n, int((t0 + seg + 1.4) * sr))
        lt = tt[i0:i1] - t0
        e = np.clip((lt + 1.0) / 1.6, 0, 1) * np.clip((seg + 1.4 - lt) / 1.6, 0, 1)
        e = np.sin(e * np.pi / 2) ** 2
        for v, m in enumerate(ch):
            for d, pan in [(-0.0016, 0.25), (0.0, 0.5), (0.0019, 0.75)]:
                fq = midi_hz(m) * (1 + d)
                ph = rng.uniform(0, 2 * np.pi)
                sig = (np.sin(2 * np.pi * fq * lt + ph) + 0.32 * np.sin(4 * np.pi * fq * lt + ph * 1.3)
                       + 0.12 * np.sin(6 * np.pi * fq * lt + ph * 0.7)) * e * 0.022
                L[i0:i1] += sig * math.cos(pan * math.pi / 2)
                R[i0:i1] += sig * math.sin(pan * math.pi / 2)
        # baixo
        fq = midi_hz(roots[s % 4] + 12)
        b = np.sin(2 * np.pi * fq * lt) * e * 0.085
        L[i0:i1] += b
        R[i0:i1] += b
    trem = 0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * tt)
    L *= trem
    R *= trem
    # arpejo
    beat = 0.6
    step = beat / 2
    pattern = [0, 2, 1, 3, 2, 4, 3, 1]
    k = 0
    st = 0.0
    while st < DUR - 1:
        ch = chords[int(st // seg) % 4]
        m = ch[pattern[k % 8]] + 12
        amp = 0.11 * float(intensity(st)) * (1.0 if k % 2 == 0 else 0.7)
        i0 = int(st * sr)
        i1 = min(n, i0 + int(1.1 * sr))
        lt = tt[i0:i1] - st
        fq = midi_hz(m)
        e = np.exp(-lt / 0.28) * np.clip(lt / 0.006, 0, 1)
        sig = (np.sin(2 * np.pi * fq * lt) + 0.28 * np.sin(4 * np.pi * fq * lt) * np.exp(-lt / 0.08)) * e * amp
        pan = 0.3 if k % 2 == 0 else 0.7
        L[i0:i1] += sig * math.cos(pan * math.pi / 2)
        R[i0:i1] += sig * math.sin(pan * math.pi / 2)
        k += 1
        st += step
    # pulso grave e chocalho
    st = 0.0
    while st < DUR - 0.5:
        I = float(intensity(st))
        ka = 0.32 * clamp((I - 0.4) / 0.6)
        if ka > 0:
            i0 = int(st * sr)
            i1 = min(n, i0 + int(0.4 * sr))
            lt = tt[i0:i1] - st
            fq = 45 + 70 * np.exp(-lt / 0.04)
            phase = 2 * np.pi * np.cumsum(fq) / sr
            kick = np.sin(phase) * np.exp(-lt / 0.16) * ka
            L[i0:i1] += kick
            R[i0:i1] += kick
        sa = 0.05 * clamp((I - 0.55) / 0.45)
        if sa > 0:
            i0 = int((st + beat / 2) * sr)
            i1 = min(n, i0 + int(0.08 * sr))
            if i1 > i0:
                lt = tt[i0:i1] - st - beat / 2
                nz = rng.standard_normal(i1 - i0)
                nz = np.diff(nz, prepend=0)
                sh = nz * np.exp(-lt / 0.025) * sa
                L[i0:i1] += sh * 0.8
                R[i0:i1] += sh
        st += beat
    # subidas antes das viradas de cena
    for tc in [T3, T6]:
        i0 = int((tc - 2.2) * sr)
        i1 = int((tc + 0.3) * sr)
        lt = tt[i0:i1] - (tc - 2.2)
        nz = rng.standard_normal(i1 - i0)
        ker = np.ones(24) / 24
        nz = np.convolve(nz, ker, mode="same")
        e = (lt / 2.2) ** 2 * np.clip((2.5 - lt) / 0.3, 0, 1)
        L[i0:i1] += nz * e * 0.12
        R[i0:i1] += nz * e * 0.12
    # reverberação simples por convolução
    ir_len = int(2.4 * sr)
    it = np.arange(ir_len) / sr
    nfft = 1 << int(math.ceil(math.log2(n + ir_len)))
    out = []
    for ch_sig, seed in [(L, 11), (R, 12)]:
        ir = np.random.default_rng(seed).standard_normal(ir_len) * np.exp(-it / 0.62)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(ch_sig, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]
        out.append(ch_sig * 0.8 + wet * 0.35)
    L, R = out
    fade = np.clip(tt / 1.5, 0, 1) * np.clip((DUR - tt) / 3.0, 0, 1)
    L *= fade
    R *= fade
    st = np.stack([L, R], axis=1)
    rms = np.sqrt(np.mean(st ** 2))
    st *= 10 ** (-16 / 20) / rms
    lim = 10 ** (-1.2 / 20)
    st = lim * np.tanh(st / lim)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


# ------------------------------------------------------------------- saída

def ffmpeg_bin():
    env_ff = os.environ.get("FFMPEG")
    if env_ff:
        return env_ff
    return shutil.which("ffmpeg") or FFMPEG_RESERVA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float, help="tempos (s) para salvar como PNG")
    ap.add_argument("--stills-dir", default=".")
    ap.add_argument("--out", default=os.path.join(REPO, "assets", "video", "ia-inovacao-simbiose.mp4"))
    ap.add_argument("--poster-t", type=float, default=21.0)
    args = ap.parse_args()

    if args.stills:
        os.makedirs(args.stills_dir, exist_ok=True)
        for t in args.stills:
            draw(t).save(os.path.join(args.stills_dir, f"quadro_{t:05.1f}.png"))
        return

    tmp = tempfile.mkdtemp(prefix="clipe_")
    wav = os.path.join(tmp, "trilha.wav")
    print("trilha...", flush=True)
    soundtrack(wav)
    cmd = [ffmpeg_bin(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", args.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(DUR * FPS)
    for i in range(total):
        p.stdin.write(draw(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"quadro {i}/{total}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg falhou")
    poster = os.path.splitext(args.out)[0] + ".jpg"
    draw(args.poster_t).save(poster, quality=85)
    shutil.rmtree(tmp, ignore_errors=True)
    print("ok:", args.out, poster)


if __name__ == "__main__":
    main()
