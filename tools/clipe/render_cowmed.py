#!/usr/bin/env python3
"""Clipe "Cowmed: a IA que escuta o rebanho", caso de sucesso do Alegrete Summit 2026.

Mesma identidade e mesmas ferramentas do clipe "IA + Inovação" (render_clipe.py):
quadros desenhados com Pillow, trilha sintetizada com numpy, montagem com ffmpeg.

Uso:
    python3 -I tools/clipe/render_cowmed.py                  # vídeo completo
    python3 -I tools/clipe/render_cowmed.py --stills 4 40    # só quadros PNG
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import numpy as np  # noqa: E402

from render_clipe import (  # noqa: E402
    AMBER, FPS, GRAY, GREEN, H, REPO, SS, W, WHITE, Frame, caption, circuits, clamp,
    ease, env, eout, ffmpeg_bin, lerp, logo, midi_hz, mix, partial, prog, sc,
)

DUR = 75.0
RED = (255, 112, 92)
T1, T2, T3, T4, T5, T6, T7, TEND = 0.0, 8.0, 18.0, 30.0, 46.0, 56.0, 66.0, DUR

FONTES = "Fontes: UFSM (2026), Forbes (2022), CNN Brasil (2026). Números da empresa marcados como autodeclarados."


# --------------------------------------------------------------- desenhos

COW = [(8, 62), (30, 48), (46, 40), (56, 44), (70, 48), (110, 42), (200, 44), (228, 48), (240, 58),
       (244, 100), (236, 118), (232, 176), (218, 176), (214, 128), (196, 124), (192, 176), (180, 176),
       (176, 130), (100, 130), (92, 176), (80, 176), (78, 128), (70, 124), (64, 176), (52, 176),
       (52, 110), (46, 88), (28, 86), (10, 80), (4, 72), (8, 62)]
COLLAR = [(73, 47), (57, 98)]


def cow(f, x, y, s, a, c=AMBER, collar=0.0, fill=0.16):
    """Vaca estilizada vista de lado, olhando para a esquerda; (x, y) é o canto superior esquerdo."""
    if a <= 0.004:
        return
    P = [(x + px * s, y + py * s) for px, py in COW]
    f.dg.polygon([(px * SS, py * SS) for px, py in P], fill=sc(c, a * fill))
    f.line(P, c, 2.4, a)
    f.line([(x + 50 * s, y + 43 * s), (x + 63 * s, y + 29 * s), (x + 61 * s, y + 45 * s)], c, 2.2, a)  # orelha
    f.line([(x + 240 * s, y + 58 * s), (x + 256 * s, y + 92 * s), (x + 254 * s, y + 130 * s)], c, 2.0, a)  # rabo
    f.dot((x + 254 * s, y + 134 * s), 4.5 * s, c, a)
    f.dot((x + 27 * s, y + 59 * s), 3.2 * s, c, a)  # olho
    for ex, ey, rx, ry in [(130, 70, 22, 14), (190, 90, 16, 12), (95, 95, 12, 9)]:  # manchas
        f.ellipse((x + ex * s, y + ey * s), rx * s, ry * s, c, a * 0.55, 1.6)
    f.line([(x + 186 * s, y + 128 * s), (x + 192 * s, y + 138 * s), (x + 204 * s, y + 138 * s),
            (x + 208 * s, y + 127 * s)], c, 1.8, a * 0.8)  # úbere
    if collar > 0:
        p0 = (x + COLLAR[0][0] * s, y + COLLAR[0][1] * s)
        p1 = (x + COLLAR[1][0] * s, y + COLLAR[1][1] * s)
        f.line(partial([p0, p1], collar), GREEN, 5.5 * s, a)
        if collar >= 1:
            bx, by = p1
            f.dg.rounded_rectangle([(bx - 9 * s) * SS, (by - 4 * s) * SS, (bx + 9 * s) * SS, (by + 14 * s) * SS],
                                   radius=int(4 * s * SS), fill=sc(GREEN, a))
    return P


def sensor_pos(x, y, s):
    return (x + COLLAR[1][0] * s, y + (COLLAR[1][1] + 5) * s)


def waves(f, p, t, a, n=3, r0=14, dr=22, c=GREEN, start=-60, end=60):
    """Ondas de sinal saindo do sensor (arcos concêntricos)."""
    for i in range(n):
        ph = (t * 0.9 + i / n) % 1.0
        r = r0 + dr * n * ph
        aa = a * (1 - ph) * 0.9
        if aa <= 0.01:
            continue
        x, y = p
        f.dg.arc([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], start, end,
                 fill=sc(c, aa), width=int(2.2 * SS))
        f.dg.arc([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], 180 + start, 180 + end,
                 fill=sc(c, aa), width=int(2.2 * SS))


def rrect(f, box, r, c, a, w=2.0, fill=None):
    if a <= 0.004:
        return
    x0, y0, x1, y1 = box
    f.dg.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=int(r * SS),
                           outline=sc(c, a), width=int(w * SS), fill=sc(fill, a) if fill else None)


def chip(f, cx, cy, txt, c, a, size=22, pad=16):
    if a <= 0.004:
        return
    wd = f.text_width(txt, "semi", size) + 2 * pad
    rrect(f, (cx - wd / 2, cy - size * 0.95, cx + wd / 2, cy + size * 0.95), size * 0.95, c, a, 1.8,
          fill=sc(c, 0.14))
    f.text((cx, cy), txt, "semi", size, WHITE, a)


def header(f, t, a0, a1, txt, c=GREEN):
    a = env(t, a0, a1, 0.6, 0.6)
    f.text_runs(W / 2, 64, [(txt, c)], "bold", 20, a, tracking=5)


def building(f, cx, cy, s, c, a):
    """Prédio universitário: frontão e colunas."""
    f.line([(cx - 60 * s, cy - 30 * s), (cx, cy - 70 * s), (cx + 60 * s, cy - 30 * s), (cx - 60 * s, cy - 30 * s)], c, 2.4, a)
    for i in range(5):
        xx = cx - 44 * s + i * 22 * s
        f.line([(xx, cy - 22 * s), (xx, cy + 34 * s)], c, 3.0, a)
    f.line([(cx - 66 * s, cy + 40 * s), (cx + 66 * s, cy + 40 * s)], c, 3.0, a)


def sprout(f, cx, cy, s, c, a, k=1.0):
    """Muda brotando dentro de um círculo: a incubadora."""
    f.ellipse((cx, cy), 62 * s, 62 * s, c, a, 2.2)
    stem = [(cx, cy + 40 * s), (cx, cy + 10 * s), (cx + 2 * s, cy - 20 * s)]
    f.line(partial(stem, k), c, 3.0, a)
    if k > 0.6:
        kk = (k - 0.6) / 0.4
        f.line(partial([(cx, cy + 2 * s), (cx - 22 * s, cy - 14 * s), (cx - 36 * s, cy - 8 * s), (cx, cy + 2 * s)], kk), c, 2.4, a)
        f.line(partial([(cx + 1 * s, cy - 8 * s), (cx + 24 * s, cy - 28 * s), (cx + 38 * s, cy - 22 * s), (cx + 1 * s, cy - 8 * s)], kk), c, 2.4, a)
    f.line([(cx - 30 * s, cy + 40 * s), (cx + 30 * s, cy + 40 * s)], c, 2.4, a)


def person(f, cx, cy, s, c, a):
    f.ellipse((cx, cy - 46 * s), 13 * s, 13 * s, c, a, 2.4)
    f.line([(cx - 26 * s, cy + 30 * s), (cx - 20 * s, cy - 18 * s), (cx + 20 * s, cy - 18 * s), (cx + 26 * s, cy + 30 * s)], c, 2.4, a)


def phone(f, cx, cy, a):
    rrect(f, (cx - 112, cy - 165, cx + 112, cy + 165), 22, WHITE, a * 0.85, 2.4)
    f.line([(cx - 22, cy - 150), (cx + 22, cy - 150)], WHITE, 3.0, a * 0.6)


def cloud(f, cx, cy, s, c, a):
    for dx, dy, r in [(-40, 8, 30), (0, -10, 40), (42, 6, 30)]:
        f.dg.arc([(cx + dx * s - r * s) * SS, (cy + dy * s - r * s) * SS, (cx + dx * s + r * s) * SS,
                  (cy + dy * s + r * s) * SS], 180, 360, fill=sc(c, a), width=int(2.4 * SS))
    f.line([(cx - 70 * s, cy + 36 * s), (cx + 72 * s, cy + 36 * s)], c, 2.4, a)


def sparkline(f, x0, y0, wd, t, seed, c, a, amp=12):
    pts = []
    for i in range(41):
        u = i / 40
        v = (math.sin(u * 9 + t * 3 + seed) * 0.6 + math.sin(u * 23 + t * 5.3 + seed * 2) * 0.4)
        pts.append((x0 + wd * u, y0 + v * amp))
    f.line(pts, c, 2.0, a)


# ---------------------------------------------------------------- mapa

AMERICA_SUL = [(-77, 8), (-72, 12), (-62, 11), (-52, 5), (-50, 0), (-44, -2), (-35, -5), (-35, -9), (-39, -14),
               (-39, -18), (-41, -22), (-48, -26), (-53, -34), (-58, -38), (-62, -39), (-65, -42), (-66, -47),
               (-68, -52), (-70, -55), (-74, -50), (-73, -42), (-71, -30), (-70, -18), (-76, -14), (-81, -6),
               (-80, -2), (-78, 2), (-77, 8)]
AMERICA_CENTRAL = [(-117, 32), (-108, 31), (-97, 26), (-97, 21), (-91, 19), (-87, 21), (-88, 16), (-83, 15),
                   (-83, 10), (-77, 8), (-79, 9), (-86, 12), (-92, 14), (-96, 16), (-105, 20), (-110, 24),
                   (-112, 29), (-117, 32)]
MAP_X0, MAP_Y0, MAP_K = 96, 96, 5.9


def proj(lon, lat):
    return (MAP_X0 + (lon + 118) * MAP_K, MAP_Y0 + (33 - lat) * MAP_K)


def inside(pt, poly):
    x, y = pt
    res = False
    for i in range(len(poly) - 1):
        (x1, y1), (x2, y2) = poly[i], poly[i + 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            res = not res
    return res


def _map_dots():
    dots = []
    lat = 32.0
    while lat > -56:
        lon = -118.0
        while lon < -34:
            if inside((lon, lat), AMERICA_SUL) or inside((lon, lat), AMERICA_CENTRAL):
                dots.append((lon, lat))
            lon += 1.9
        lat -= 1.9
    return dots


MAP_DOTS = _map_dots()
SANTA_MARIA = (-53.8, -29.7)
PAISES = [("Paraguai", (-58.0, -23.4)), ("Uruguai", (-56.2, -33.0)), ("México", (-102.0, 23.0))]


# ------------------------------------------------------------------ cenas

def scene1(f, t):
    a = env(t, T1, T2, 0.4, 0.7)
    logo(f, W / 2, 96, 58, prog(t, 0.3, 1.8), a)
    k = ease(prog(t, 1.0, 1.8))
    f.text_runs(W / 2, 170, [("CASOS DE SUCESSO", GREEN), ("  ·  ", GRAY), ("IA NO BRASIL", AMBER)], "bold", 20,
                a * k, tracking=5)
    k2 = ease(prog(t, 1.6, 2.5))
    f.text_runs(W / 2, 246 + (1 - k2) * 14, [("Cowmed", WHITE)], "russo", 92, a * k2, glow=0.25)
    k3 = ease(prog(t, 2.3, 3.2))
    f.text_runs(W / 2, 322 + (1 - k3) * 10, [("a IA que ", WHITE), ("escuta", GREEN), (" o rebanho", AMBER)],
                "semi", 38, a * k3)
    kc = ease(prog(t, 2.8, 4.0))
    cx, cy, s = W / 2 - 126 * 1.25, 400, 1.25
    cow(f, cx, cy, s, a * kc, collar=ease(prog(t, 3.6, 4.6)))
    if t > 4.6:
        waves(f, sensor_pos(cx, cy, s), t, a * ease(prog(t, 4.6, 5.4)))


def scene2(f, t):
    a = env(t, T2, T3, 0.6, 0.7)
    header(f, t, T2, T3, "ORIGEM")
    k = ease(prog(t, 8.4, 9.2))
    f.text_runs(W / 2, 130, [("Santa Maria", WHITE), (" (RS)", AMBER)], "semi", 40, a * k)
    xs = [330, 640, 950]
    y = 330
    building(f, xs[0], y, 1.0, AMBER, a * ease(prog(t, 8.8, 9.8)))
    sprout(f, xs[1], y, 1.0, GREEN, a * ease(prog(t, 12.6, 13.4)), ease(prog(t, 12.8, 14.2)))
    cs = 0.62
    cow(f, xs[2] - 128 * cs, y - 62, cs, a * ease(prog(t, 15.0, 15.8)), collar=ease(prog(t, 15.4, 16.2)))
    for i, lab, c, t0 in [(0, "UFSM", AMBER, 9.4), (1, "Pulsar", GREEN, 13.2), (2, "Cowmed", WHITE, 15.6)]:
        f.text((xs[i], y + 92), lab, "bold", 28, c, a * ease(prog(t, t0, t0 + 0.6)))
    for (x0, x1, t0) in [(xs[0] + 90, xs[1] - 90, 11.8), (xs[1] + 90, xs[2] - 100, 14.4)]:
        kk = ease(prog(t, t0, t0 + 0.9))
        if kk > 0:
            f.line(partial([(x0, y), (x1, y)], kk), GREEN, 2.4, a)
            if kk >= 1:
                f.line([(x1 - 12, y - 9), (x1, y), (x1 - 12, y + 9)], GREEN, 2.4, a)
            px = x0 + (x1 - x0) * ((t * 0.7) % 1.0)
            if kk >= 1:
                f.dot((px, y), 4, GREEN, a)
    caption(f, t, 9.6, 13.4, None, y=560, size=32, runs=[("Nasceu como projeto de estudantes da ", WHITE), ("UFSM", AMBER)])
    caption(f, t, 13.4, T3 - 0.1, None, y=560, size=30,
            runs=[("Incubada e graduada na ", WHITE), ("Pulsar", GREEN), (", a incubadora tecnológica da UFSM", WHITE)])


HERD = [(150, 330), (370, 300), (590, 335), (810, 305), (1010, 335)]


def scene3(f, t):
    a = env(t, T3, T4, 0.6, 0.7)
    header(f, t, T3, T4, "O PROBLEMA", AMBER)
    hy = 470
    f.line([(60, hy), (W - 60, hy)], AMBER, 1.6, a * 0.45)
    s = 0.62
    sick = 3
    for i, (x, y) in enumerate(HERD):
        kk = ease(prog(t, 18.4 + i * 0.25, 19.2 + i * 0.25))
        late = ease(prog(t, 23.2, 24.0))
        c = mix(AMBER, RED, late) if i == sick else AMBER
        cow(f, x, y + 30, s, a * kk, c=c)
        if i == sick and late > 0:
            bx, by = x + 40 * s, y + 4
            f.ellipse((bx, by), 16, 16, RED, a * late, 2.4)
            f.text((bx, by), "!", "bold", 24, RED, a * late)
    # olho do produtor varrendo o rebanho
    px = 640 + 520 * math.sin(t * 0.9)
    ke = ease(prog(t, 19.0, 19.8)) * (1 - ease(prog(t, 23.0, 23.6)))
    if ke > 0:
        f.ellipse((px, 220), 30, 15, WHITE, a * ke * 0.8, 2.2)
        f.dot((px, 220), 7, WHITE, a * ke * 0.8)
    # perdas
    kl = ease(prog(t, 25.6, 26.6))
    if kl > 0:
        for j, lab in enumerate(["leite", "R$"]):
            x = 520 + j * 240
            yy = 180 + 30 * eout(prog(t, 25.6, 27.0))
            f.text((x, yy), lab, "bold", 34, RED, a * kl)
            f.line([(x + 50, yy - 18), (x + 50, yy + 18)], RED, 2.6, a * kl)
            f.line([(x + 41, yy + 8), (x + 50, yy + 18), (x + 59, yy + 8)], RED, 2.6, a * kl)
    caption(f, t, 19.2, 23.4, "Sem dados, o produtor depende de observar o rebanho.", y=580, size=30)
    caption(f, t, 23.6, T4 - 0.1, None, y=580, size=31,
            runs=[("Cio e doença percebidos tarde", AMBER), (" = ", WHITE), ("leite e dinheiro perdidos.", RED)])


METRICAS = ["ruminação", "alimentação", "atividade", "ofegância"]


def scene4(f, t):
    a = env(t, T4, T5, 0.6, 0.7)
    header(f, t, T4, T5, "A SOLUÇÃO COM IA")
    cx, cy, s = 70, 250, 1.5
    cow(f, cx, cy, s, a * ease(prog(t, 30.2, 31.0)), collar=ease(prog(t, 30.8, 31.6)))
    sp = sensor_pos(cx, cy, s)
    if t > 31.6:
        waves(f, sp, t, a * ease(prog(t, 31.6, 32.2)), dr=18)
    k = ease(prog(t, 31.8, 32.6))
    f.text_runs(250, 150, [("25", GREEN), (" leituras por segundo", WHITE)], "semi", 32, a * k, glow=0.0)
    xx = 70
    for i, m in enumerate(METRICAS):
        kk = ease(prog(t, 32.6 + i * 0.35, 33.2 + i * 0.35))
        wd = f.text_width(m, "semi", 19) + 24
        chip(f, xx + wd / 2, 585, m, GREEN, a * kk, size=19, pad=12)
        xx += wd + 14
    # dados até a nuvem
    cl = (720, 210)
    path = [(sp[0] + 20, sp[1]), (sp[0] + 120, sp[1] - 60), (cl[0] - 140, cl[1] + 36), (cl[0] - 72, cl[1] + 36)]
    kp = ease(prog(t, 34.0, 35.2))
    if kp > 0:
        f.line(partial(path, kp), GREEN, 1.6, a * 0.5)
        if kp >= 1:
            for j in range(5):
                u = ((t * 0.5) + j / 5) % 1.0
                q = partial(path, u)[-1]
                f.dot(q, 3.5, GREEN, a)
    kc = ease(prog(t, 34.8, 35.6))
    cloud(f, cl[0], cl[1], 1.0, GREEN, a * kc)
    f.text((cl[0], cl[1] + 20), "IA", "bold", 28, GREEN, a * kc)
    f.text((cl[0], cl[1] + 74), "Vic, a IA própria da empresa", "med", 19, GRAY, a * kc)
    for j in range(4):
        sparkline(f, 600, 330 + j * 38, 240, t + j, j * 1.7, mix(GREEN, AMBER, j / 3), a * kc * 0.7, amp=9)
    # celular com alertas
    ph = (1080, 365)
    kph = ease(prog(t, 36.0, 36.8))
    phone(f, ph[0], ph[1], a * kph)
    kpath = ease(prog(t, 36.4, 37.2))
    if kpath > 0:
        f.line(partial([(cl[0] + 76, cl[1]), (ph[0] - 40, cl[1]), (ph[0] - 40, ph[1] - 120)], kpath), GREEN, 1.6, a * 0.5)
    f.text((ph[0], ph[1] - 112), "ALERTA", "bold", 20, AMBER, a * ease(prog(t, 37.0, 37.6)))
    for j, lab in enumerate(["cio", "saúde", "estresse térmico"]):
        kk = ease(prog(t, 37.4 + j * 0.45, 38.0 + j * 0.45))
        yy = ph[1] - 60 + j * 62
        rrect(f, (ph[0] - 96, yy - 22, ph[0] + 96, yy + 22), 10, AMBER, a * kk, 1.6, fill=(40, 28, 10))
        f.dot((ph[0] - 78, yy), 5, AMBER, a * kk)
        f.text((ph[0] - 64, yy), lab, "semi", 19, WHITE, a * kk, anchor="lm")
    caption(f, t, 38.4, 42.2, "Alerta no celular antes dos sinais clínicos.", y=660, size=30)
    caption(f, t, 42.2, T5 - 0.1, None, y=660, size=31,
            runs=[("A IA transforma ", WHITE), ("movimento", AMBER), (" em ", WHITE), ("diagnóstico precoce", GREEN), (".", WHITE)])


def scene5(f, t):
    a = env(t, T5, T6, 0.6, 0.7)
    header(f, t, T5, T6, "VALIDAÇÃO  ·  2022")
    # 547 investidores como pontos
    kd = prog(t, 46.6, 49.0)
    cols, rows = 46, 12
    x0, y0, gap = W / 2 - (cols - 1) * 12 / 2, 120, 12
    shown = int(547 * ease(kd))
    for i in range(min(shown, cols * rows)):
        r, c = divmod(i, cols)
        f.dot((x0 + c * gap, y0 + r * gap), 2.2, GREEN, a * 0.55)
    k1 = ease(prog(t, 47.0, 47.8))
    f.text_runs(W / 2, 330 + (1 - k1) * 12, [("R$ 5,9 milhões", GREEN)], "russo", 72, a * k1, glow=0.3)
    f.text((W / 2, 398), "de 547 investidores", "semi", 32, WHITE, a * ease(prog(t, 47.8, 48.5)))
    f.text((W / 2, 462), "recorde em equity crowdfunding no Brasil", "semi", 30, AMBER, a * ease(prog(t, 49.4, 50.2)))
    k3 = ease(prog(t, 51.2, 52.0))
    f.text_runs(W / 2, 560, [("35 mil vacas", WHITE), (" em mais de ", GRAY), ("400 fazendas", WHITE)], "semi", 36, a * k3)
    f.text((W - 70, 676), "Forbes, 2022", "med", 18, GRAY, a * k1, anchor="rm")


def scene6(f, t):
    a = env(t, T6, T7, 0.6, 0.7)
    header(f, t, T6, T7, "ESCALA  ·  2026")
    km = ease(prog(t, 56.2, 57.4))
    for lon, lat in MAP_DOTS:
        f.dot(proj(lon, lat), 2.0, GREEN, a * km * 0.32)
    sm = proj(*SANTA_MARIA)
    ks = ease(prog(t, 57.0, 57.8))
    f.dot(sm, 7, AMBER, a * ks)
    r = 10 + 26 * ((t * 0.8) % 1.0)
    f.ellipse(sm, r, r, AMBER, a * ks * (1 - (t * 0.8) % 1.0), 2.0)
    f.text((sm[0] + 16, sm[1] - 16), "Santa Maria (RS)", "med", 17, AMBER, a * ks, anchor="lm")
    for i, (nome, ll) in enumerate(PAISES):
        kk = ease(prog(t, 61.2 + i * 0.5, 62.0 + i * 0.5))
        if kk <= 0:
            continue
        p = proj(*ll)
        dx, dy = p[0] - sm[0], p[1] - sm[1]
        mid = ((sm[0] + p[0]) / 2 + dy * 0.25, (sm[1] + p[1]) / 2 - dx * 0.25)
        arc = [lerp(lerp(sm, mid, u), lerp(mid, p, u), u) for u in [j / 20 for j in range(21)]]
        f.line(partial(arc, kk), GREEN, 1.8, a * 0.8)
        if kk >= 1:
            f.node(p, 7, GREEN, a)
            anchor = "rm" if nome == "Paraguai" else "lm"
            oy = 12 if nome == "Uruguai" else 0
            f.text((p[0] + (-14 if anchor == "rm" else 14), p[1] + oy), nome, "semi", 19, WHITE, a, anchor=anchor)
    rx = 930
    k1 = ease(prog(t, 57.6, 58.4))
    f.text_runs(rx, 210 + (1 - k1) * 12, [("100 mil", GREEN)], "russo", 84, a * k1, glow=0.3)
    f.text((rx, 280), "animais monitorados", "semi", 34, WHITE, a * k1)
    k2 = ease(prog(t, 59.4, 60.2))
    f.text((rx, 360), "Receita de cerca de R$ 18 milhões", "semi", 29, WHITE, a * k2)
    f.text((rx, 398), "em 2025 (autodeclarado)", "med", 24, GRAY, a * k2)
    k3 = ease(prog(t, 61.4, 62.4))
    f.text_runs(rx, 480, [("Paraguai", AMBER), ("  ·  ", GRAY), ("Uruguai", AMBER), ("  ·  ", GRAY), ("México", AMBER)],
                "semi", 30, a * k3)
    f.text((W - 70, 676), "CNN Brasil, 2026", "med", 18, GRAY, a * k1, anchor="rm")


def scene7(f, t):
    a = env(t, T7, TEND + 1, 0.6, 0.1) * (1 - ease(prog(t, 73.6, 74.9)))
    header(f, t, T7, TEND + 1, "A LIÇÃO", AMBER)
    parts = [("Problema do campo", AMBER), ("Ciência da universidade", WHITE), ("Incubadora regional", GREEN)]
    size = 25
    wds = [f.text_width(p, "semi", size) + 40 for p, _ in parts]
    gap = 54
    total = sum(wds) + gap * 2
    x = W / 2 - total / 2
    for i, ((p, c), wd) in enumerate(zip(parts, wds)):
        kk = ease(prog(t, 66.3 + i * 0.6, 67.0 + i * 0.6))
        chip(f, x + wd / 2, 170, p, c, a * kk, size=size, pad=20)
        if i < 2:
            f.text((x + wd + gap / 2, 170), "+", "bold", 34, WHITE, a * kk)
        x += wd + gap
    ka = ease(prog(t, 68.4, 69.0))
    f.line(partial([(W / 2, 214), (W / 2, 262)], ka), WHITE, 2.4, a * 0.8)
    if ka >= 1:
        f.line([(W / 2 - 10, 252), (W / 2, 262), (W / 2 + 10, 252)], WHITE, 2.4, a * 0.8)
    k2 = ease(prog(t, 68.8, 69.8))
    f.text_runs(W / 2, 318 + (1 - k2) * 12, [("IA que sai do ", WHITE), ("Pampa", AMBER), (" para o ", WHITE), ("mundo", GREEN), (".", WHITE)],
                "semi", 48, a * k2)
    k3 = ease(prog(t, 70.6, 71.6))
    logo(f, W / 2, 438, 70, prog(t, 70.4, 71.8), a)
    f.text_runs(W / 2, 520, [("ALEGRETE SUMMIT 2026", WHITE)], "bold", 26, a * k3, tracking=3)
    f.text_runs(W / 2, 562, [("Inovar é ", WHITE), ("construir pontes", GREEN), (".", WHITE)], "semi", 26, a * k3)
    f.text((W / 2, 680), FONTES, "med", 16, GRAY, a * ease(prog(t, 69.4, 70.2)))


def draw(t):
    f = Frame()
    fade = 1 - ease(prog(t, 73.6, 74.9))
    dim = 1.0 if t < T2 or t > T7 else 0.45
    circuits(f, prog(t, 0.0, 2.6), dim * fade)
    for fn, a, b in [(scene1, T1, T2 + 0.1), (scene2, T2 - 0.1, T3 + 0.1), (scene3, T3 - 0.1, T4 + 0.1),
                     (scene4, T4 - 0.1, T5 + 0.1), (scene5, T5 - 0.1, T6 + 0.1), (scene6, T6 - 0.1, T7 + 0.1),
                     (scene7, T7 - 0.1, TEND)]:
        if a <= t <= b:
            fn(f, t)
    return f.render()


# ------------------------------------------------------------------ trilha

def intensity(t):
    keys = [(0, 0.05), (8, 0.2), (17.5, 0.3), (24, 0.35), (29.5, 0.5), (31, 0.85), (45.5, 0.8),
            (50, 0.7), (56, 0.9), (65.5, 0.95), (70, 0.45), (75, 0.0)]
    xs, ys = zip(*keys)
    return np.interp(t, xs, ys)


def soundtrack(path, sr=48000):
    """Trilha mais pastoral que a do primeiro clipe: tom maior, 84 bpm, dedilhado."""
    n = int(DUR * sr)
    tt = np.arange(n) / sr
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(21)
    beat = 60 / 84
    seg = beat * 8
    chords = [[55, 59, 62, 67, 71], [52, 55, 59, 64, 67], [48, 55, 60, 64, 67], [50, 54, 57, 62, 66]]  # G Em C D
    roots = [31, 28, 36, 38]
    nseg = int(math.ceil(DUR / seg))
    for s in range(nseg):
        ch = chords[s % 4]
        t0 = s * seg
        i0 = int(max(0, t0 - 1.0) * sr)
        i1 = min(n, int((t0 + seg + 1.4) * sr))
        lt = tt[i0:i1] - t0
        e = np.clip((lt + 1.0) / 1.8, 0, 1) * np.clip((seg + 1.4 - lt) / 1.8, 0, 1)
        e = np.sin(e * np.pi / 2) ** 2
        for m in ch:
            for d, pan in [(-0.0012, 0.3), (0.0014, 0.7)]:
                fq = midi_hz(m) * (1 + d)
                ph = rng.uniform(0, 2 * np.pi)
                sig = (np.sin(2 * np.pi * fq * lt + ph) + 0.18 * np.sin(4 * np.pi * fq * lt + ph)) * e * 0.02
                L[i0:i1] += sig * math.cos(pan * math.pi / 2)
                R[i0:i1] += sig * math.sin(pan * math.pi / 2)
        fq = midi_hz(roots[s % 4] + 12)
        b = np.sin(2 * np.pi * fq * lt) * e * 0.08
        L[i0:i1] += b
        R[i0:i1] += b
    # dedilhado (corda pinçada com harmônicos que decaem rápido)
    step = beat / 2
    pattern = [0, 2, 4, 2, 1, 3, 4, 3]
    k, st = 0, 0.0
    while st < DUR - 1:
        ch = chords[int(st // seg) % 4]
        m = ch[pattern[k % 8]] + 12
        amp = 0.12 * (0.35 + 0.65 * float(intensity(st))) * (1.0 if k % 2 == 0 else 0.75)
        i0 = int(st * sr)
        i1 = min(n, i0 + int(1.4 * sr))
        lt = tt[i0:i1] - st
        fq = midi_hz(m)
        e = np.exp(-lt / 0.45) * np.clip(lt / 0.004, 0, 1)
        sig = (np.sin(2 * np.pi * fq * lt) + 0.5 * np.sin(4 * np.pi * fq * lt) * np.exp(-lt / 0.12)
               + 0.25 * np.sin(6 * np.pi * fq * lt) * np.exp(-lt / 0.06)) * e * amp
        pan = 0.35 if k % 2 == 0 else 0.65
        L[i0:i1] += sig * math.cos(pan * math.pi / 2)
        R[i0:i1] += sig * math.sin(pan * math.pi / 2)
        k += 1
        st += step
    # pulso suave
    st = 0.0
    while st < DUR - 0.5:
        I = float(intensity(st))
        ka = 0.26 * clamp((I - 0.45) / 0.55)
        if ka > 0:
            i0 = int(st * sr)
            i1 = min(n, i0 + int(0.4 * sr))
            lt = tt[i0:i1] - st
            fq = 50 + 60 * np.exp(-lt / 0.04)
            kick = np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.exp(-lt / 0.15) * ka
            L[i0:i1] += kick
            R[i0:i1] += kick
        st += beat
    for tc in [T4, T6]:
        i0 = int((tc - 2.0) * sr)
        i1 = int((tc + 0.3) * sr)
        lt = tt[i0:i1] - (tc - 2.0)
        nz = np.convolve(rng.standard_normal(i1 - i0), np.ones(30) / 30, mode="same")
        e = (lt / 2.0) ** 2 * np.clip((2.3 - lt) / 0.3, 0, 1)
        L[i0:i1] += nz * e * 0.1
        R[i0:i1] += nz * e * 0.1
    ir_len = int(2.6 * sr)
    it = np.arange(ir_len) / sr
    nfft = 1 << int(math.ceil(math.log2(n + ir_len)))
    out = []
    for sig, seed in [(L, 31), (R, 32)]:
        ir = np.random.default_rng(seed).standard_normal(ir_len) * np.exp(-it / 0.7)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(sig, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]
        out.append(sig * 0.8 + wet * 0.38)
    L, R = out
    fade = np.clip(tt / 1.5, 0, 1) * np.clip((DUR - tt) / 3.0, 0, 1)
    stereo = np.stack([L * fade, R * fade], axis=1)
    stereo *= 10 ** (-16 / 20) / np.sqrt(np.mean(stereo ** 2))
    lim = 10 ** (-1.2 / 20)
    stereo = lim * np.tanh(stereo / lim)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((stereo * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------- saída

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--stills-dir", default=".")
    ap.add_argument("--out", default=os.path.join(REPO, "assets", "video", "cowmed-ia.mp4"))
    ap.add_argument("--poster-t", type=float, default=39.5)
    args = ap.parse_args()
    if args.stills:
        os.makedirs(args.stills_dir, exist_ok=True)
        for t in args.stills:
            draw(t).save(os.path.join(args.stills_dir, f"quadro_{t:05.1f}.png"))
        return
    tmp = tempfile.mkdtemp(prefix="cowmed_")
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
        if i % 300 == 0:
            print(f"quadro {i}/{total}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg falhou")
    draw(args.poster_t).save(os.path.splitext(args.out)[0] + ".jpg", quality=85)
    shutil.rmtree(tmp, ignore_errors=True)
    print("ok:", args.out)


if __name__ == "__main__":
    main()
