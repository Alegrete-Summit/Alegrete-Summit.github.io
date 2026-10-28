#!/usr/bin/env python3
"""Clipe-chamada do Alegrete Summit 2026, para o destaque da página inicial.

Vertical 4:5 (720x900), também serve para o feed do Instagram. Mesma identidade e
mesmas ferramentas dos outros clipes (render_clipe.py), mais fotos da edição de 2025.
Gera uma versão por idioma, com os textos desenhados no próprio quadro.

Uso:
    python3 -I tools/clipe/render_chamada.py                     # pt, en e es
    python3 -I tools/clipe/render_chamada.py --lang en           # só um idioma
    python3 -I tools/clipe/render_chamada.py --stills 3 9 24     # só quadros PNG
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile
import wave

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import numpy as np  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402

import render_clipe as rc  # noqa: E402
from render_clipe import (  # noqa: E402
    AMBER, FPS, GRAY, GREEN, REPO, SS, WHITE, caption, circuits, clamp, ease, env, eout, lerp, logo,
    midi_hz, mix, partial, prog, sc,
)

# formato vertical: as funções de render_clipe leem W e H do próprio módulo
W, H = 720, 900
rc.W, rc.H = W, H
rc.CIRCUITS = rc._circuit_paths()

DUR = 50.0
T1, T2, T3, T4, T5, T6, T7, TEND = 0.0, 5.5, 12.5, 20.5, 31.5, 38.5, 42.5, DUR
BAND = 420  # altura da faixa de foto no topo
IMG = os.path.join(REPO, "assets", "img", "2025")
SAIDA = {"pt": "alegrete-summit-2026", "en": "alegrete-summit-2026.en", "es": "alegrete-summit-2026.es"}

TXT = {
    "pt": {
        "data": "29 e 30 de outubro  ·  Alegrete/RS",
        "gancho": ["Tem uma ideia?", "Um projeto, um negócio, uma pesquisa?", "A conexão que falta", "pode estar no Summit."],
        "pontes": "INOVAR É CONSTRUIR PONTES",
        "pares": [("quem produz", "quem pesquisa"), ("quem empreende", "quem investe"), ("o campo", "a cidade")],
        "porque": ["Por que participar?", "Aqui, esses mundos se encontram."],
        "espera": "O QUE TE ESPERA",
        "cards": [("18", "conversas no Palco Geek", "carreira, games, comunicação e IA"),
                  ("13", "equipes no Bye Bye Boss", "pitches de 3 minutos, com prêmios"),
                  ("1 dia", "de Ideathon", "desafios do território viram soluções"),
                  ("2 dias", "de Mostra Tecnológica", "robótica, IA e impressão 3D")],
        "foto": "Alegrete Summit 2025",
        "conexoes": ["Ideias encontram parceiros.", "Conexões viram negócios.", "Uma conversa pode virar sociedade."],
        "quem": "PARA QUEM É?",
        "publico": ["Estudantes", "Pesquisadores", "Empreendedores", "Investidores", "Produtores rurais", "Gestores públicos"],
        "voce": "Para você.",
        "dia": "29 e 30 de outubro",
        "local": "Sicredi Essência  ·  Alegrete/RS",
        "chips": ["Gratuito", "Certificado de 24 h"],
        "lema": [("Inovar é ", WHITE), ("construir pontes", GREEN), (".", WHITE)],
        "inscr": "Pré-inscrição: link na bio do",
    },
    "en": {
        "data": "October 29 and 30  ·  Alegrete, Brazil",
        "gancho": ["Got an idea?", "A project, a business, a research question?", "The connection you're missing", "may be at the Summit."],
        "pontes": "INNOVATING IS BUILDING BRIDGES",
        "pares": [("who produces", "who researches"), ("who starts up", "who invests"), ("the countryside", "the city")],
        "porque": ["Why take part?", "This is where these worlds meet."],
        "espera": "WHAT AWAITS YOU",
        "cards": [("18", "talks on the Geek Stage", "careers, games, communication and AI"),
                  ("13", "teams at Bye Bye Boss", "3-minute pitches, with prizes"),
                  ("1 day", "of Ideathon", "local challenges become solutions"),
                  ("2 days", "of Technology Showcase", "robotics, AI and 3D printing")],
        "foto": "Alegrete Summit 2025",
        "conexoes": ["Ideas meet partners.", "Connections become business.", "One conversation can become a partnership."],
        "quem": "WHO IS IT FOR?",
        "publico": ["Students", "Researchers", "Entrepreneurs", "Investors", "Farmers", "Public managers"],
        "voce": "For you.",
        "dia": "October 29 and 30",
        "local": "Sicredi Essência  ·  Alegrete, Brazil",
        "chips": ["Free", "24-hour certificate"],
        "lema": [("Innovating is ", WHITE), ("building bridges", GREEN), (".", WHITE)],
        "inscr": "Pre-registration: link in the bio of",
    },
    "es": {
        "data": "29 y 30 de octubre  ·  Alegrete/RS",
        "gancho": ["¿Tienes una idea?", "¿Un proyecto, un negocio, una investigación?", "La conexión que te falta", "puede estar en el Summit."],
        "pontes": "INNOVAR ES CONSTRUIR PUENTES",
        "pares": [("quien produce", "quien investiga"), ("quien emprende", "quien invierte"), ("el campo", "la ciudad")],
        "porque": ["¿Por qué participar?", "Aquí, esos mundos se encuentran."],
        "espera": "LO QUE TE ESPERA",
        "cards": [("18", "charlas en el Escenario Geek", "carrera, juegos, comunicación e IA"),
                  ("13", "equipos en el Bye Bye Boss", "pitches de 3 minutos, con premios"),
                  ("1 día", "de Ideathon", "desafíos del territorio se vuelven soluciones"),
                  ("2 días", "de Muestra Tecnológica", "robótica, IA e impresión 3D")],
        "foto": "Alegrete Summit 2025",
        "conexoes": ["Las ideas encuentran socios.", "Las conexiones se vuelven negocios.", "Una charla puede volverse una sociedad."],
        "quem": "¿PARA QUIÉN ES?",
        "publico": ["Estudiantes", "Investigadores", "Emprendedores", "Inversores", "Productores rurales", "Gestores públicos"],
        "voce": "Para ti.",
        "dia": "29 y 30 de octubre",
        "local": "Sicredi Essência  ·  Alegrete/RS",
        "chips": ["Gratuito", "Certificado de 24 h"],
        "lema": [("Innovar es ", WHITE), ("construir puentes", GREEN), (".", WHITE)],
        "inscr": "Preinscripción: enlace en la bio de",
    },
}


# ------------------------------------------------------------------ fotos

def _cover(path, box, size):
    im = Image.open(path).convert("RGB")
    if box:
        im = im.crop(box)
    return im.resize(size, Image.LANCZOS)


# (arquivo, recorte sem os textos das artes do Instagram)
FOTOS = {
    "estudantes": ("publico-estudantes.jpg", (0, 50, 720, 455)),
    "palco": ("palco-principal.jpg", None),
    "pitch": ("empreendedores.jpg", (0, 50, 720, 455)),
    "ideathon": ("faca-parte.jpg", (0, 480, 1080, 1088)),
    "mostra": ("mostra-exoesqueleto.jpg", (0, 0, 610, 343)),
    "painel": ("painel.jpg", (0, 190, 720, 1090)),
}
_fotos = {}


def foto(nome):
    """Foto em 110% do tamanho final, para o zoom lento."""
    if nome not in _fotos:
        arq, box = FOTOS[nome]
        size = (W, H) if nome == "painel" else (W, BAND)
        _fotos[nome] = _cover(os.path.join(IMG, arq), box, (int(size[0] * 1.1), int(size[1] * 1.1)))
    return _fotos[nome]


def _mask(h, solid):
    """Opaco até a fração `solid` da altura e depois esmaece até o preto."""
    y = np.arange(h) / h
    m = 1 - ease_np((y - solid) / (1 - solid))
    return m[:, None, None].astype(np.float32)


def ease_np(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


_masks = {}


class PFrame(rc.Frame):
    """Quadro com uma camada de fotos por baixo da geometria e do texto."""

    def __init__(self):
        super().__init__()
        self.bg = np.zeros((H, W, 3), np.float32)

    def photo(self, nome, a, k, dark=1.0, solid=0.62):
        """Desenha a foto com zoom k (0..1) e opacidade a."""
        if a <= 0.004:
            return
        im = foto(nome)
        tw, th = (W, H) if nome == "painel" else (W, BAND)
        z = 1.1 - 0.1 * (1 - ease(k))  # 1.0 → 1.1
        cw, ch = im.width / z * 1.0, im.height / z * 1.0
        x0, y0 = (im.width - cw) / 2, (im.height - ch) / 2
        crop = im.resize((tw, th), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        key = (th, solid)
        if key not in _masks:
            _masks[key] = _mask(th, solid)
        arr = np.asarray(crop, np.float32) * _masks[key] * (a * dark)
        self.bg[:th] = np.maximum(self.bg[:th], arr)

    def render(self):
        base = self.g.reduce(SS)
        arr = np.asarray(base, dtype=np.float32)
        g1 = base.reduce(2).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
        g2 = base.reduce(8).filter(ImageFilter.GaussianBlur(2.5)).resize((W, H), Image.BICUBIC)
        out = self.bg + arr + 0.85 * np.asarray(g1, np.float32) + 1.6 * np.asarray(g2, np.float32)
        im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        im.alpha_composite(self.t)
        return im.convert("RGB")


# --------------------------------------------------------------- desenhos

def fit(f, s, fnt, size, maxw=640):
    """Maior tamanho até `size` em que o texto cabe em `maxw`."""
    while size > 12 and f.text_width(s, fnt, size) > maxw:
        size -= 1
    return size


def rrect(f, box, r, c, a, w=2.0, fill=None):
    if a <= 0.004:
        return
    x0, y0, x1, y1 = box
    f.dg.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=int(r * SS),
                           outline=sc(c, a), width=int(w * SS), fill=sc(fill, a) if fill else None)


def chip(f, cx, cy, txt, c, a, size=22, pad=16):
    if a <= 0.004:
        return 0
    wd = f.text_width(txt, "semi", size) + 2 * pad
    rrect(f, (cx - wd / 2, cy - size * 0.95, cx + wd / 2, cy + size * 0.95), size * 0.95, c, a, 1.8,
          fill=sc(c, 0.14))
    f.text((cx, cy), txt, "semi", size, WHITE, a)
    return wd


def header(f, t, a0, a1, txt, y, c=GREEN, size=22):
    a = env(t, a0, a1, 0.6, 0.6)
    size = fit(f, txt + " " * len(txt), "bold", size, 600)
    f.text_runs(W / 2, y, [(txt, c)], "bold", size, a, tracking=4)


def line_in(f, t, t0, y, runs, fnt, size, a, glow=0.0, maxw=640):
    k = ease(prog(t, t0, t0 + 0.7))
    if k <= 0:
        return
    size = fit(f, "".join(s for s, _ in runs), fnt, size, maxw)
    f.text_runs(W / 2, y + (1 - k) * 14, runs, fnt, size, a * k, glow=glow)


# ------------------------------------------------------------------ cenas

def scene1(f, t, L):
    a = env(t, T1, T2, 0.3, 0.6)
    cx = W / 2
    logo(f, cx, 300, 170, prog(t, 0.5, 2.6), a)
    k = ease(prog(t, 2.0, 2.9))
    f.text_runs(cx, 470 + (1 - k) * 12, [("ALEGRETE", WHITE)], "russo", 62, a * k, tracking=4)
    k2 = ease(prog(t, 2.4, 3.3))
    f.text_runs(cx, 530, [("SUMMIT", WHITE)], "med", 30, a * k2, tracking=14)
    k3 = ease(prog(t, 2.8, 3.6))
    f.text_runs(cx, 576, [("2026", GREEN)], "bold", 28, a * k3, glow=0.5, tracking=10)
    k4 = ease(prog(t, 3.4, 4.2))
    f.text((cx, 668 + (1 - k4) * 10), L["data"], "semi", fit(f, L["data"], "semi", 25), AMBER, a * k4)


def scene2(f, t, L):
    a = env(t, T2, T3, 0.6, 0.6)
    f.photo("estudantes", a * ease(prog(t, 5.5, 6.5)), prog(t, T2, T3))
    g = L["gancho"]
    line_in(f, t, 6.2, 500, [(g[0], WHITE)], "russo", 54, a, glow=0.15)
    line_in(f, t, 7.2, 562, [(g[1], GRAY)], "semi", 26, a)
    line_in(f, t, 8.9, 676, [(g[2], WHITE)], "semi", 38, a)
    line_in(f, t, 9.5, 726, [(g[3], GREEN)], "semi", 38, a, glow=0.2)


def arch_y(x, x0=110, x1=610, top=330, base=470):
    u = (x - x0) / (x1 - x0)
    return base - (base - top) * 4 * u * (1 - u)


def scene3(f, t, L):
    a = env(t, T3, T4, 0.6, 0.6)
    header(f, t, T3, T4, L["pontes"], 120)
    deck = 470
    # pilares e tabuleiro
    kp = ease(prog(t, 12.8, 13.6))
    for x in (110, 610):
        f.line(partial([(x, 580), (x, deck - 6)], kp), WHITE, 4.0, a * 0.85)
    kd = ease(prog(t, 13.2, 14.2))
    f.line(partial([(60, deck), (660, deck)], kd), WHITE, 3.0, a * 0.85)
    # arco e tirantes
    ka = ease(prog(t, 13.6, 14.8))
    arc = [(x, arch_y(x)) for x in range(110, 611, 10)]
    f.line(partial(arc, ka), GREEN, 3.6, a)
    for i, x in enumerate(range(160, 600, 50)):
        kk = ease(prog(t, 14.2 + i * 0.05, 14.6 + i * 0.05))
        f.line(partial([(x, arch_y(x)), (x, deck)], kk), GREEN, 1.6, a * 0.6)
    # pulsos atravessando nos dois sentidos
    if t > 14.8:
        ap = a * ease(prog(t, 14.8, 15.3))
        for j in range(4):
            u = (t * 0.32 + j / 4) % 1.0
            f.dot((80 + 560 * u, deck - 10), 4.5, GREEN, ap)
            f.dot((640 - 560 * u, deck - 22), 4.5, AMBER, ap * 0.9)
    # pares de cada lado da ponte
    for i, (esq, dir_) in enumerate(L["pares"]):
        t0 = 14.6 + i * 2.0
        t1 = t0 + 2.0 if i < 2 else T4
        kk = env(t, t0, t1, 0.4, 0.4)
        if kk <= 0:
            continue
        size = min(fit(f, esq, "semi", 22, 280), fit(f, dir_, "semi", 22, 280))
        chip(f, 170, 520, esq, AMBER, a * kk, size=size, pad=14)
        chip(f, 550, 520, dir_, GREEN, a * kk, size=size, pad=14)
    for x, c in ((110, AMBER), (610, GREEN)):
        f.node((x, 590), 8, c, a * kp)
    p = L["porque"]
    line_in(f, t, 15.4, 700, [(p[0], AMBER)], "semi", 34, a)
    line_in(f, t, 16.0, 752, [(p[1], WHITE)], "semi", 30, a)


CARD_FOTOS = ["palco", "pitch", "ideathon", "mostra"]
CARD = 2.75


def scene4(f, t, L):
    a = env(t, T4, T5, 0.5, 0.6)
    for i, (num, tit, sub) in enumerate(L["cards"]):
        t0 = T4 + i * CARD
        kk = env(t, t0 - (0.0 if i == 0 else 0.25), t0 + CARD + (0.0 if i == 3 else 0.25), 0.5, 0.5)
        if kk <= 0:
            continue
        f.photo(CARD_FOTOS[i], a * kk, prog(t, t0 - 0.3, t0 + CARD + 0.3))
        kt = ease(prog(t, t0 + 0.1, t0 + 0.7)) * (1 - ease(prog(t, t0 + CARD - 0.3, t0 + CARD)) if i < 3 else 1)
        dy = (1 - kt) * 16
        f.text_runs(W / 2, 590 + dy, [(num, GREEN)], "russo", 92, a * kt, glow=0.3)
        f.text((W / 2, 672 + dy), tit, "semi", fit(f, tit, "semi", 36), WHITE, a * kt)
        f.text((W / 2, 718 + dy), sub, "med", fit(f, sub, "med", 24), GRAY, a * kt)
        f.text((W - 24, BAND - 22), L["foto"], "med", 14, GRAY, a * kk * 0.9, anchor="rm")
    header(f, t, T4, T5, L["espera"], 484, AMBER, 20)
    # indicador de progresso
    for i in range(4):
        on = T4 + i * CARD <= t < T4 + (i + 1) * CARD or (i == 3 and t >= T5 - 0.1)
        f.dot((W / 2 - 45 + i * 30, 800), 5 if on else 3.5, GREEN if on else GRAY, a * (1 if on else 0.6))


def _rede():
    rng = np.random.default_rng(2026)
    pts = []
    while len(pts) < 30:
        p = (rng.uniform(70, 650), rng.uniform(130, 560))
        if all(math.dist(p, q) > 70 for q in pts):
            pts.append(p)
    edges = sorted(((i, j) for i in range(len(pts)) for j in range(i + 1, len(pts))
                    if math.dist(pts[i], pts[j]) < 150), key=lambda e: math.dist(pts[e[0]], pts[e[1]]))
    order = list(rng.permutation(len(edges)))
    return pts, [edges[k] for k in order]


REDE_PTS, REDE_EDGES = _rede()
NEGOCIOS = REDE_EDGES[3:24:7]  # três ligações que viram negócio


def scene5(f, t, L):
    a = env(t, T5, T6, 0.6, 0.6)
    for i, p in enumerate(REDE_PTS):
        kk = ease(prog(t, 31.6 + (i % 10) * 0.08, 32.2 + (i % 10) * 0.08))
        f.node(p, 7, WHITE if i % 3 else AMBER, a * kk * 0.85)
    m = len(REDE_EDGES)
    for k, (i, j) in enumerate(REDE_EDGES):
        kk = ease(prog(t, 32.2 + 2.2 * k / m, 32.7 + 2.2 * k / m))
        f.line(partial([REDE_PTS[i], REDE_PTS[j]], kk), GREEN, 1.4, a * 0.45)
        if kk >= 1 and k % 4 == 0:
            u = (t * 0.6 + k * 0.173) % 1.0
            f.dot(lerp(REDE_PTS[i], REDE_PTS[j], u), 3.0, mix(GREEN, WHITE, 0.5), a * 0.8)
    for k, (i, j) in enumerate(NEGOCIOS):
        kk = ease(prog(t, 34.6 + k * 0.4, 35.2 + k * 0.4))
        if kk <= 0:
            continue
        p, q = REDE_PTS[i], REDE_PTS[j]
        f.line([p, q], AMBER, 4.0, a * kk)
        for pt in (p, q):
            f.node(pt, 10, AMBER, a * kk, core=WHITE)
            r = 12 + 22 * ((t * 0.8 + k * 0.3) % 1.0)
            f.ellipse(pt, r, r, AMBER, a * kk * (1 - (t * 0.8 + k * 0.3) % 1.0), 2.0)
    c = L["conexoes"]
    line_in(f, t, 32.6, 650, [(c[0], WHITE)], "semi", 38, a)
    line_in(f, t, 34.4, 712, [(c[1], GREEN)], "russo", 40, a, glow=0.25)
    line_in(f, t, 35.8, 780, [(c[2], GRAY)], "med", 24, a)


def scene6(f, t, L):
    a = env(t, T6, T7, 0.4, 0.5)
    header(f, t, T6, T7, L["quem"], 120, AMBER)
    for i, p in enumerate(L["publico"]):
        t0 = 38.7 + i * 0.32
        kk = ease(prog(t, t0, t0 + 0.4))
        c = GREEN if i % 2 == 0 else WHITE
        x = W / 2 + (1 - eout(prog(t, t0, t0 + 0.5))) * (60 if i % 2 else -60)
        f.text((x, 210 + i * 66), p, "semi", 40, c, a * kk)
    k = ease(prog(t, 40.9, 41.5))
    f.text_runs(W / 2, 680 + (1 - k) * 14, [(L["voce"], AMBER)], "russo", 68, a * k, glow=0.3)


def scene7(f, t, L):
    a = env(t, T7, TEND + 1, 0.6, 0.1) * (1 - ease(prog(t, 48.6, 49.9)))
    f.photo("painel", a * ease(prog(t, 42.5, 43.5)), prog(t, T7, TEND), dark=0.22, solid=0.55)
    logo(f, W / 2, 170, 110, prog(t, 42.7, 44.0), a)
    k1 = ease(prog(t, 43.4, 44.2))
    f.text_runs(W / 2, 270, [("ALEGRETE SUMMIT 2026", WHITE)], "bold", 32, a * k1, tracking=3)
    k2 = ease(prog(t, 43.9, 44.7))
    f.text_runs(W / 2, 352 + (1 - k2) * 12, [(L["dia"], GREEN)], "russo", fit(f, L["dia"], "russo", 48), a * k2, glow=0.3)
    f.text((W / 2, 410), L["local"], "semi", fit(f, L["local"], "semi", 26), WHITE, a * k2)
    k3 = ease(prog(t, 44.6, 45.3))
    c0, c1 = L["chips"]
    w0 = f.text_width(c0, "semi", 24) + 36
    w1 = f.text_width(c1, "semi", 24) + 36
    x = W / 2 - (w0 + w1 + 20) / 2
    chip(f, x + w0 / 2, 500, c0, GREEN, a * k3, size=24, pad=18)
    chip(f, x + w0 + 20 + w1 / 2, 500, c1, AMBER, a * k3, size=24, pad=18)
    k4 = ease(prog(t, 45.2, 46.0))
    f.text_runs(W / 2, 600, L["lema"], "semi", 30, a * k4)
    k5 = ease(prog(t, 45.8, 46.6))
    f.text((W / 2, 720), L["inscr"], "med", fit(f, L["inscr"], "med", 24), GRAY, a * k5)
    f.text_runs(W / 2, 762, [("@alegretecidadeinovadora", GREEN)], "bold", 32, a * k5, glow=0.25)


def draw(t, L):
    f = PFrame()
    fade = 1 - ease(prog(t, 48.6, 49.9))
    dim = 1.0 if t < T2 or t > T7 else 0.4
    circuits(f, prog(t, 0.0, 2.4), dim * fade)
    for fn, a, b in [(scene1, T1, T2 + 0.1), (scene2, T2 - 0.1, T3 + 0.1), (scene3, T3 - 0.1, T4 + 0.1),
                     (scene4, T4 - 0.1, T5 + 0.1), (scene5, T5 - 0.1, T6 + 0.1), (scene6, T6 - 0.1, T7 + 0.1),
                     (scene7, T7 - 0.1, TEND)]:
        if a <= t <= b:
            fn(f, t, L)
    return f.render()


# ------------------------------------------------------------------ trilha

def intensity(t):
    keys = [(0, 0.15), (5.5, 0.4), (12.5, 0.6), (20.0, 0.75), (20.5, 1.0), (31.5, 0.9), (38.5, 1.0),
            (42.5, 0.75), (47, 0.5), (50, 0.0)]
    xs, ys = zip(*keys)
    return np.interp(t, xs, ys)


def soundtrack(path, sr=48000):
    """Trilha animada: tom maior, 112 bpm, I–V–vi–IV, arpejo, bumbo, palmas e chimbal."""
    n = int(DUR * sr)
    tt = np.arange(n) / sr
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(29)
    beat = 60 / 112
    seg = beat * 4
    chords = [[60, 64, 67, 72], [59, 62, 67, 71], [57, 60, 64, 69], [57, 60, 65, 69]]  # C G Am F
    roots = [36, 43, 45, 41]
    nseg = int(math.ceil(DUR / seg))

    def put(i0, sig, pan=0.5):
        i1 = min(n, i0 + len(sig))
        L[i0:i1] += sig[:i1 - i0] * math.cos(pan * math.pi / 2)
        R[i0:i1] += sig[:i1 - i0] * math.sin(pan * math.pi / 2)

    for s in range(nseg):
        ch = chords[s % 4]
        t0 = s * seg
        i0 = int(max(0, t0 - 0.3) * sr)
        i1 = min(n, int((t0 + seg + 0.6) * sr))
        lt = tt[i0:i1] - t0
        e = np.clip((lt + 0.3) / 0.5, 0, 1) * np.clip((seg + 0.6 - lt) / 0.8, 0, 1)
        e = np.sin(e * np.pi / 2) ** 2
        for m in ch:
            for d, pan in [(-0.0015, 0.25), (0.0015, 0.75)]:
                fq = midi_hz(m) * (1 + d)
                ph = rng.uniform(0, 2 * np.pi)
                sig = (np.sin(2 * np.pi * fq * lt + ph) + 0.3 * np.sin(4 * np.pi * fq * lt + ph)
                       + 0.12 * np.sin(6 * np.pi * fq * lt + ph)) * e * 0.016
                L[i0:i1] += sig * math.cos(pan * math.pi / 2)
                R[i0:i1] += sig * math.sin(pan * math.pi / 2)
        # baixo em colcheias
        for k in range(8):
            st = t0 + k * beat / 2
            if st >= DUR - 0.3:
                break
            I = float(intensity(st))
            j0 = int(st * sr)
            lt2 = np.arange(int(0.26 * sr)) / sr
            fq = midi_hz(roots[s % 4] + (12 if k % 4 == 3 else 0))
            b = (np.sin(2 * np.pi * fq * lt2) + 0.3 * np.sin(4 * np.pi * fq * lt2)) * np.exp(-lt2 / 0.16)
            put(j0, b * np.clip(lt2 / 0.005, 0, 1) * 0.11 * (0.4 + 0.6 * I))
    # arpejo
    step = beat / 4
    k, st = 0, 0.0
    pattern = [0, 1, 2, 3, 2, 1, 2, 3]
    while st < DUR - 0.8:
        I = float(intensity(st))
        if I > 0.35:
            ch = chords[int(st // seg) % 4]
            m = ch[pattern[k % 8]] + 12
            j0 = int(st * sr)
            lt = np.arange(int(0.5 * sr)) / sr
            fq = midi_hz(m)
            e = np.exp(-lt / 0.16) * np.clip(lt / 0.003, 0, 1)
            sig = (np.sin(2 * np.pi * fq * lt) + 0.35 * np.sin(4 * np.pi * fq * lt) * np.exp(-lt / 0.05)) * e
            put(j0, sig * 0.06 * (I - 0.3) / 0.7 * (1.0 if k % 2 == 0 else 0.7), 0.3 if k % 2 == 0 else 0.7)
        k += 1
        st += step
    # bateria
    k, st = 0, 0.0
    while st < DUR - 0.5:
        I = float(intensity(st))
        j0 = int(st * sr)
        if I > 0.3:
            lt = np.arange(int(0.4 * sr)) / sr
            fq = 48 + 90 * np.exp(-lt / 0.03)
            kick = np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.exp(-lt / 0.14)
            put(j0, kick * 0.42 * clamp((I - 0.3) / 0.6))
        if I > 0.55 and k % 2 == 1:
            lt = np.arange(int(0.25 * sr)) / sr
            nz = rng.standard_normal(len(lt))
            nz = nz - np.convolve(nz, np.ones(6) / 6, mode="same")
            clap = nz * np.exp(-lt / 0.05) * (1 + 0.6 * (lt < 0.012))
            put(j0, clap * 0.13 * clamp((I - 0.55) / 0.4), 0.55)
        if I > 0.45:
            lt = np.arange(int(0.08 * sr)) / sr
            for off, amp in [(beat / 2, 1.0), (beat * 0.75, 0.45)]:
                nz = rng.standard_normal(len(lt))
                nz = nz - np.convolve(nz, np.ones(3) / 3, mode="same")
                put(int((st + off) * sr), nz * np.exp(-lt / 0.018) * 0.05 * amp * clamp((I - 0.45) / 0.5), 0.7)
        k += 1
        st += beat
    # subidas antes das viradas de cena
    for tc in [T4, T7]:
        i0 = int((tc - 1.8) * sr)
        i1 = int((tc + 0.2) * sr)
        lt = tt[i0:i1] - (tc - 1.8)
        nz = np.convolve(rng.standard_normal(i1 - i0), np.ones(20) / 20, mode="same")
        e = (lt / 1.8) ** 2 * np.clip((2.0 - lt) / 0.2, 0, 1)
        L[i0:i1] += nz * e * 0.14
        R[i0:i1] += nz * e * 0.14
    ir_len = int(1.8 * sr)
    it = np.arange(ir_len) / sr
    nfft = 1 << int(math.ceil(math.log2(n + ir_len)))
    out = []
    for sig, seed in [(L, 41), (R, 42)]:
        ir = np.random.default_rng(seed).standard_normal(ir_len) * np.exp(-it / 0.45)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(sig, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]
        out.append(sig * 0.85 + wet * 0.25)
    L, R = out
    fade = np.clip(tt / 0.8, 0, 1) * np.clip((DUR - tt) / 2.5, 0, 1)
    stereo = np.stack([L * fade, R * fade], axis=1)
    stereo *= 10 ** (-15 / 20) / np.sqrt(np.mean(stereo ** 2))
    lim = 10 ** (-1.2 / 20)
    stereo = lim * np.tanh(stereo / lim)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((stereo * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------- saída

def render(lang, wav, outdir, poster_t):
    L = TXT[lang]
    out = os.path.join(outdir, SAIDA[lang] + ".mp4")
    cmd = [rc.ffmpeg_bin(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(DUR * FPS)
    for i in range(total):
        p.stdin.write(draw(i / FPS, L).tobytes())
        if i % 300 == 0:
            print(f"{lang}: quadro {i}/{total}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg falhou")
    draw(poster_t, L).save(os.path.join(outdir, SAIDA[lang] + ".jpg"), quality=85)
    print("ok:", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=list(TXT), action="append")
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--stills-dir", default=".")
    ap.add_argument("--outdir", default=os.path.join(REPO, "assets", "video"))
    ap.add_argument("--poster-t", type=float, default=47.0)
    args = ap.parse_args()
    langs = args.lang or list(TXT)
    if args.stills:
        os.makedirs(args.stills_dir, exist_ok=True)
        for lang in langs:
            for t in args.stills:
                draw(t, TXT[lang]).save(os.path.join(args.stills_dir, f"{lang}_{t:05.1f}.png"))
        return
    with tempfile.TemporaryDirectory(prefix="chamada_") as tmp:
        wav = os.path.join(tmp, "trilha.wav")
        print("trilha...", flush=True)
        soundtrack(wav)
        for lang in langs:
            render(lang, wav, args.outdir, args.poster_t)


if __name__ == "__main__":
    main()
