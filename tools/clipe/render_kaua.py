#!/usr/bin/env python3
"""Clipe "Kauã e o poder de criar", fábula do Alegrete Summit 2026.

Um jovem indígena no meio da Amazônia ganha internet via satélite, um notebook
e acesso a um modelo de IA, cria um produto para a floresta e transforma a aldeia.
Personagem e produto são fictícios.

Ilustração plana desenhada com Pillow (supersampling 2x), trilha e efeitos
sintetizados com numpy, montagem com ffmpeg. Os textos são desenhados no quadro,
então há uma versão por idioma.

Uso:
    python3 -I tools/clipe/render_kaua.py                    # pt, en e es
    python3 -I tools/clipe/render_kaua.py --lang en          # só um idioma
    python3 -I tools/clipe/render_kaua.py --stills 20 60 --stills-dir /tmp/quadros
"""
import argparse
import math
import multiprocessing as mp
import os
import random
import subprocess
import sys
import tempfile
import wave
from functools import lru_cache

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from render_clipe import (  # noqa: E402
    AMBER, FPS, GRAY, GREEN, H, REPO, W, WHITE, clamp, ease, env, eout, ffmpeg_bin, font, lerp,
    midi_hz, mix, partial, prog,
)

SS = 2
DUR = 174.0
# cenas: abertura, aldeia (mata + antena), notebook, IA, Kaá Sentinela, sucesso, aldeia nova, moral, fim
T_ALDEIA, T_NOTE, T_IA, T_KAA, T_MUNDO, T_NOVA, T_MORAL, T_FIM = 8.0, 50.0, 64.0, 96.0, 110.0, 128.0, 146.0, 166.0
CORTES = [T_ALDEIA, T_NOTE, T_IA, T_KAA, T_MUNDO, T_NOVA, T_MORAL, T_FIM]

INK = (10, 14, 18)
RED = (232, 72, 58)
SKIN = (152, 98, 62)
HAIR = (24, 20, 18)
URUCUM = (214, 50, 34)
SHORTS = (40, 54, 96)
SHIRT = (22, 176, 112)
STRAW = (196, 152, 84)
SOIL = (146, 106, 66)
WATER = (58, 128, 160)
PANEL = (44, 82, 150)

SAIDA = {"pt": "kaua-ia", "en": "kaua-ia.en", "es": "kaua-ia.es"}

TXT = {
    "pt": {
        "pre": "ALEGRETE SUMMIT 2026 apresenta",
        "sub": "e o poder de criar",
        "tag": "Uma fábula sobre internet, IA e transformação",
        "c1": "No coração da Amazônia, longe das grandes cidades, vive Kauã.",
        "c2": "Ele conhece cada trilha, cada planta e cada som da mata.",
        "c3": "Mas a floresta está em perigo: motosserras ilegais e queimadas avançam.",
        "c4": "E a aldeia vive desconectada do mundo.",
        "nosignal": "sem sinal",
        "c5": "Um dia, chega à aldeia uma antena de internet via satélite, como a Starlink.",
        "c6": "Satélites em órbita baixa levam a internet até o meio da mata.",
        "c7": "Pela primeira vez, a aldeia está conectada ao mundo.",
        "box": "inclusão digital",
        "c8": "Depois, um projeto de inclusão digital entrega um notebook a Kauã.",
        "c9": "Ele nunca estudou computação. Mas tem curiosidade e um problema real para resolver.",
        "placeholder": "Escreva sua mensagem…",
        "u1": "Não sou programador. Como posso proteger a floresta de motosserras e queimadas?",
        "a1": "Vamos construir juntos, passo a passo. Ideia: celulares usados com painel solar, presos nas árvores, "
              "escutam a mata. Um modelo de IA reconhece o som de motosserra e de fogo e avisa a aldeia na hora.",
        "u2": "Como eu ensino a IA a reconhecer esses sons?",
        "a2": "Grave sons da mata com o celular. Eu escrevo o código com você, testamos juntos e corrigimos o que der errado.",
        "test": "Teste do modelo",
        "classes": ["motosserra", "fogo", "chuva", "pássaros"],
        "c10": "Kauã descreve o problema do seu jeito, na sua língua.",
        "c11": "A IA não sabe o que ele sabe sobre a mata. Mas sabe programar.",
        "c12": "Juntos, eles planejam, programam, testam e corrigem.",
        "c13": "Ele entra com o conhecimento da floresta. A IA, com a técnica.",
        "kaa": "kaá: mata, em tupi",
        "c14": "Nasce o Kaá Sentinela: sensores solares que escutam a mata.",
        "c15": "Ao ouvir uma motosserra, a IA avisa a aldeia em segundos.",
        "detect": "motosserra · 97%",
        "alert": "ALERTA",
        "alert_body": "Motosserra a 2,3 km ao norte",
        "protected": "Floresta protegida",
        "c16": "Outras aldeias querem o Kaá. Depois, ONGs, governos e empresas do mundo todo.",
        "c17": "Em poucos meses, vira sucesso internacional, e Kauã fica milionário.",
        "countries": ["Peru", "Colômbia", "México", "Canadá", "Noruega", "Alemanha", "Quênia", "Congo", "Índia",
                      "Indonésia", "Japão", "Austrália"],
        "n_paises": "países", "n_com": "comunidades", "n_rev": "faturamento",
        "money": lambda v: "R$ " + (f"{v:.1f}".replace(".", ",") + " milhões" if v >= 1 else f"{v * 1000:.0f} mil"),
        "c18": "Com o dinheiro, Kauã investiu na aldeia.",
        "c19": "Energia solar, água potável, posto de saúde e escola conectada.",
        "c20": "Agora, outros jovens da aldeia também criam soluções.",
        "up": ["energia solar", "água potável", "posto de saúde", "escola conectada"],
        "eq": ["internet", "notebook", "IA", "poder de criar"],
        "m1": "Qualquer pessoa, em qualquer lugar, pode criar empresas, produtos e transformar realidades.",
        "m2": "Criar soluções digitais não é mais privilégio de quem é da computação ou de quem tem muito dinheiro.",
        "m3": "Criar soluções para problemas locais pode ser o grande diferencial.",
        "end": [("Internet e IA ", WHITE), ("democratizam", GREEN), (" o poder de ", WHITE), ("criar", AMBER), (".", WHITE)],
        "date": "29 e 30 de outubro · Alegrete/RS",
        "lema": [("Inovar é ", WHITE), ("construir pontes", GREEN), (".", WHITE)],
        "fiction": "Uma fábula: personagem e produto fictícios.",
    },
    "en": {
        "pre": "ALEGRETE SUMMIT 2026 presents",
        "sub": "and the power to create",
        "tag": "A fable about the internet, AI and transformation",
        "c1": "In the heart of the Amazon, far from the big cities, lives Kauã.",
        "c2": "He knows every trail, every plant and every sound of the forest.",
        "c3": "But the forest is in danger: illegal chainsaws and fires are advancing.",
        "c4": "And the village is cut off from the world.",
        "nosignal": "no signal",
        "c5": "One day, a satellite internet antenna, like Starlink, arrives in the village.",
        "c6": "Low-orbit satellites bring the internet into the middle of the forest.",
        "c7": "For the first time, the village is connected to the world.",
        "box": "digital inclusion",
        "c8": "Then a digital inclusion project gives Kauã a laptop.",
        "c9": "He never studied computing. But he has curiosity and a real problem to solve.",
        "placeholder": "Write a message…",
        "u1": "I'm not a programmer. How can I protect the forest from chainsaws and fires?",
        "a1": "Let's build it together, step by step. Idea: used phones with solar panels, strapped to trees, "
              "listen to the forest. An AI model recognizes the sound of chainsaws and fire and alerts the village right away.",
        "u2": "How do I teach the AI to recognize those sounds?",
        "a2": "Record forest sounds with your phone. I'll write the code with you, we'll test it together and fix whatever goes wrong.",
        "test": "Model test",
        "classes": ["chainsaw", "fire", "rain", "birds"],
        "c10": "Kauã describes the problem his own way, in his own language.",
        "c11": "The AI doesn't know what he knows about the forest. But it knows how to code.",
        "c12": "Together, they plan, code, test and fix.",
        "c13": "He brings the knowledge of the forest. The AI brings the technique.",
        "kaa": "kaá: forest, in Tupi",
        "c14": "Kaá Sentinela is born: solar sensors that listen to the forest.",
        "c15": "When it hears a chainsaw, the AI alerts the village within seconds.",
        "detect": "chainsaw · 97%",
        "alert": "ALERT",
        "alert_body": "Chainsaw 2.3 km to the north",
        "protected": "Forest protected",
        "c16": "Other villages want Kaá. Then NGOs, governments and companies around the world.",
        "c17": "Within a few months it is an international hit, and Kauã becomes a millionaire.",
        "countries": ["Peru", "Colombia", "Mexico", "Canada", "Norway", "Germany", "Kenya", "Congo", "India",
                      "Indonesia", "Japan", "Australia"],
        "n_paises": "countries", "n_com": "communities", "n_rev": "revenue",
        "money": lambda v: "R$ " + (f"{v:.1f} million" if v >= 1 else f"{v * 1000:.0f} thousand"),
        "c18": "With the money, Kauã invested in his village.",
        "c19": "Solar power, clean water, a health post and a connected school.",
        "c20": "Now other young people in the village create solutions too.",
        "up": ["solar power", "clean water", "health post", "connected school"],
        "eq": ["internet", "laptop", "AI", "power to create"],
        "m1": "Anyone, anywhere, can create companies and products and transform realities.",
        "m2": "Building digital solutions is no longer a privilege of computer people or of those with lots of money.",
        "m3": "Creating solutions for local problems can be the great differentiator.",
        "end": [("The internet and AI ", WHITE), ("democratize", GREEN), (" the power to ", WHITE), ("create", AMBER), (".", WHITE)],
        "date": "October 29–30 · Alegrete, RS, Brazil",
        "lema": [("Innovating is ", WHITE), ("building bridges", GREEN), (".", WHITE)],
        "fiction": "A fable: fictional character and product.",
    },
    "es": {
        "pre": "ALEGRETE SUMMIT 2026 presenta",
        "sub": "y el poder de crear",
        "tag": "Una fábula sobre internet, IA y transformación",
        "c1": "En el corazón de la Amazonía, lejos de las grandes ciudades, vive Kauã.",
        "c2": "Conoce cada sendero, cada planta y cada sonido de la selva.",
        "c3": "Pero la selva está en peligro: avanzan las motosierras ilegales y los incendios.",
        "c4": "Y la aldea vive desconectada del mundo.",
        "nosignal": "sin señal",
        "c5": "Un día llega a la aldea una antena de internet satelital, como Starlink.",
        "c6": "Satélites de órbita baja llevan internet hasta el medio de la selva.",
        "c7": "Por primera vez, la aldea está conectada al mundo.",
        "box": "inclusión digital",
        "c8": "Después, un proyecto de inclusión digital le entrega un portátil a Kauã.",
        "c9": "Nunca estudió computación. Pero tiene curiosidad y un problema real que resolver.",
        "placeholder": "Escribe tu mensaje…",
        "u1": "No soy programador. ¿Cómo puedo proteger la selva de las motosierras y los incendios?",
        "a1": "Construyámoslo juntos, paso a paso. Idea: celulares usados con panel solar, sujetos a los árboles, "
              "escuchan la selva. Un modelo de IA reconoce el sonido de motosierras y fuego y avisa a la aldea al instante.",
        "u2": "¿Cómo le enseño a la IA a reconocer esos sonidos?",
        "a2": "Graba sonidos de la selva con tu celular. Escribo el código contigo, lo probamos juntos y corregimos lo que falle.",
        "test": "Prueba del modelo",
        "classes": ["motosierra", "fuego", "lluvia", "pájaros"],
        "c10": "Kauã describe el problema a su manera, en su propio idioma.",
        "c11": "La IA no sabe lo que él sabe de la selva. Pero sabe programar.",
        "c12": "Juntos planifican, programan, prueban y corrigen.",
        "c13": "Él aporta el conocimiento de la selva. La IA, la técnica.",
        "kaa": "kaá: selva, en tupí",
        "c14": "Nace Kaá Sentinela: sensores solares que escuchan la selva.",
        "c15": "Al oír una motosierra, la IA avisa a la aldea en segundos.",
        "detect": "motosierra · 97%",
        "alert": "ALERTA",
        "alert_body": "Motosierra a 2,3 km al norte",
        "protected": "Selva protegida",
        "c16": "Otras aldeas quieren Kaá. Después, ONG, gobiernos y empresas de todo el mundo.",
        "c17": "En pocos meses es un éxito internacional, y Kauã se vuelve millonario.",
        "countries": ["Perú", "Colombia", "México", "Canadá", "Noruega", "Alemania", "Kenia", "Congo", "India",
                      "Indonesia", "Japón", "Australia"],
        "n_paises": "países", "n_com": "comunidades", "n_rev": "facturación",
        "money": lambda v: "R$ " + (f"{v:.1f}".replace(".", ",") + " millones" if v >= 1 else f"{v * 1000:.0f} mil"),
        "c18": "Con el dinero, Kauã invirtió en su aldea.",
        "c19": "Energía solar, agua potable, puesto de salud y escuela conectada.",
        "c20": "Ahora, otros jóvenes de la aldea también crean soluciones.",
        "up": ["energía solar", "agua potable", "puesto de salud", "escuela conectada"],
        "eq": ["internet", "portátil", "IA", "poder de crear"],
        "m1": "Cualquier persona, en cualquier lugar, puede crear empresas y productos y transformar realidades.",
        "m2": "Crear soluciones digitales ya no es privilegio de quienes son de computación o de quienes tienen mucho dinero.",
        "m3": "Crear soluciones para problemas locales puede ser el gran diferencial.",
        "end": [("Internet e IA ", WHITE), ("democratizan", GREEN), (" el poder de ", WHITE), ("crear", AMBER), (".", WHITE)],
        "date": "29 y 30 de octubre · Alegrete/RS",
        "lema": [("Innovar es ", WHITE), ("construir puentes", GREEN), (".", WHITE)],
        "fiction": "Una fábula: personaje y producto ficticios.",
    },
}

HEADLINES = ["Indigenous youth protects the rainforest with AI", "Joven indígena protege la selva con IA",
             "Jovem indígena cria IA que protege a floresta", "Un jeune autochtone protège la forêt avec l'IA"]


# ---------------------------------------------------------------- utilidades

def rgba(c, a=1.0):
    return (int(c[0]), int(c[1]), int(c[2]), int(255 * clamp(a)))


def dim(c, k):
    return tuple(int(v * k) for v in c)


def wrap(s, f, size, maxw):
    fnt = font(f, size)
    lines, cur = [], ""
    for w in s.split():
        nxt = (cur + " " + w).strip()
        if fnt.getlength(nxt) <= maxw or not cur:
            cur = nxt
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bump(t, a, b, fi=0.4, fo=0.4):
    return env(t, a, b, fi, fo)


class Cv:
    """Quadro em 2x para as formas (com mistura de alfa) e textos adiados, desenhados em 1x."""

    def __init__(self, bg=None):
        self.im = bg.copy() if bg is not None else Image.new("RGB", (W * SS, H * SS), INK)
        self.d = ImageDraw.Draw(self.im, "RGBA")
        self.txt = []
        self.post = []

    @staticmethod
    def P(pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, c, a=1.0, outline=None, w=0):
        if a <= 0.004:
            return
        self.d.polygon(self.P(pts), fill=rgba(c, a), outline=rgba(outline, a) if outline else None,
                       width=int(w * SS))

    def line(self, pts, c, w=2.0, a=1.0):
        if a <= 0.004 or len(pts) < 2:
            return
        self.d.line(self.P(pts), fill=rgba(c, a), width=max(1, int(round(w * SS))), joint="curve")

    def circ(self, p, r, c, a=1.0, w=0):
        if a <= 0.004 or r <= 0:
            return
        x, y = p[0] * SS, p[1] * SS
        r *= SS
        if w:
            self.d.ellipse([x - r, y - r, x + r, y + r], outline=rgba(c, a), width=max(1, int(w * SS)))
        else:
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=rgba(c, a))

    def ell(self, p, rx, ry, c, a=1.0, w=0):
        if a <= 0.004:
            return
        x, y = p[0] * SS, p[1] * SS
        box = [x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS]
        if w:
            self.d.ellipse(box, outline=rgba(c, a), width=max(1, int(w * SS)))
        else:
            self.d.ellipse(box, fill=rgba(c, a))

    def rect(self, box, c, a=1.0, r=0, outline=None, w=0):
        if a <= 0.004:
            return
        x0, y0, x1, y1 = box
        if x1 <= x0 or y1 <= y0:
            return
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=int(r * SS), fill=rgba(c, a) if c else None,
                                 outline=rgba(outline, a) if outline else None, width=int(w * SS))

    def arc(self, p, r, a0, a1, c, w=2.0, a=1.0):
        if a <= 0.004 or r <= 0:
            return
        x, y = p[0] * SS, p[1] * SS
        r *= SS
        self.d.arc([x - r, y - r, x + r, y + r], a0, a1, fill=rgba(c, a), width=max(1, int(w * SS)))

    def glow(self, p, r, c, a=1.0, n=7):
        for i in range(n):
            k = (i + 1) / n
            self.circ(p, r * (1.15 - k), c, a * 0.11 * k)

    def shade(self, c, a, box=None):
        """Véu de cor sobre o quadro todo (noite, transições)."""
        if a <= 0.004:
            return
        x0, y0, x1, y1 = box or (0, 0, W, H)
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=rgba(c, a))

    def paste(self, layer, dx=0, dy=0):
        self.im.paste(layer, (int(round(dx * SS)), int(round(dy * SS))), layer)

    # textos (desenhados depois da redução para 1x)
    def text(self, xy, s, f, size, c, a=1.0, anchor="mm"):
        if a > 0.004 and s:
            self.txt.append(("t", xy, s, f, size, c, a, anchor))

    def runs(self, cx, y, runs, f, size, a=1.0):
        if a <= 0.004:
            return
        fnt = font(f, size)
        x = cx - sum(fnt.getlength(s) for s, _ in runs) / 2
        for s, c in runs:
            self.text((x, y), s, f, size, c, a, anchor="lm")
            x += fnt.getlength(s)

    def text_box(self, box, c, a=1.0, r=0, outline=None, w=0):
        """Retângulo desenhado na camada dos textos (fica acima das formas)."""
        if a > 0.004:
            self.txt.append(("r", box, c, a, r, outline, w))

    def render(self, black=0.0):
        out = self.im.reduce(SS)
        d = ImageDraw.Draw(out, "RGBA")
        for op in self.txt:
            if op[0] == "t":
                _, xy, s, f, size, c, a, anchor = op
                d.text(xy, s, font=font(f, size), fill=rgba(c, a), anchor=anchor)
            else:
                _, box, c, a, r, outline, w = op
                d.rounded_rectangle(box, radius=int(r), fill=rgba(c, a) if c else None,
                                    outline=rgba(outline, a) if outline else None, width=int(w))
        if black > 0.004:
            d.rectangle([0, 0, W, H], fill=(0, 0, 0, int(255 * clamp(black))))
        return out


def caption(cv, t, a0, a1, s, y=664, size=29, c=WHITE):
    a = env(t, a0, a1, 0.4, 0.4)
    if a <= 0:
        return
    lines = wrap(s, "semi", size, 1160)
    lh = size * 1.28
    y0 = y - (len(lines) - 1) * lh / 2
    fnt = font("semi", size)
    wd = max(fnt.getlength(l) for l in lines)
    cv.text_box((W / 2 - wd / 2 - 22, y0 - lh / 2 - 8, W / 2 + wd / 2 + 22, y0 + (len(lines) - 0.5) * lh + 8),
                (6, 10, 12), a * 0.72, r=14)
    dy = (1 - eout(prog(t, a0, a0 + 0.5))) * 8
    for i, l in enumerate(lines):
        cv.text((W / 2, y0 + i * lh + dy), l, "semi", size, c, a)


def logo(cv, cx, cy, size, k, a, c=GREEN):
    """Triângulo do Alegrete Summit (mesma geometria do render_clipe.logo), em traço chapado."""
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
        cv.line(partial(pts, kk), c, w, a)
        cv.circ(pts[0], w * 0.5, c, a)
        if kk >= 1:
            for n in nodes:
                cv.circ(pts[n], size * 0.07, c, a)


# ------------------------------------------------------------ fundos fixos

def gradient(top, bottom, y0=0, y1=H):
    ys = np.clip((np.arange(H * SS) / SS - y0) / (y1 - y0), 0, 1)[:, None]
    col = np.array(top, np.float32) * (1 - ys) + np.array(bottom, np.float32) * ys
    arr = np.repeat(col[:, None, :], W * SS, axis=1)
    return Image.fromarray(arr.astype(np.uint8))


SKIES = {
    "day": ((112, 186, 226), (255, 216, 160)),
    "dusk": ((52, 46, 104), (246, 132, 84)),
    "night": ((5, 9, 26), (20, 34, 68)),
    "space": ((3, 5, 12), (10, 18, 34)),
}


@lru_cache(None)
def sky(name):
    top, bot = SKIES[name]
    return gradient(top, bot, 0, 520)


def sky_at(k):
    """k = 0 dia, 1 entardecer, 2 noite."""
    if k <= 0:
        return sky("day")
    if k >= 2:
        return sky("night")
    if k <= 1:
        return Image.blend(sky("day"), sky("dusk"), k)
    return Image.blend(sky("dusk"), sky("night"), k - 1)


def palm(d, x, base, h, col, rng, lean):
    top = (x + lean, base - h)
    pts = [lerp((x, base), top, u) for u in [i / 8 for i in range(9)]]
    pts = [(px + math.sin(u * 3) * lean * 0.15, py) for (px, py), u in zip(pts, [i / 8 for i in range(9)])]
    d.line([(px * SS, py * SS) for px, py in pts], fill=col, width=int(7 * SS))
    for j in range(8):
        th = math.pi * (1.05 + j * 0.13) + rng.uniform(-0.1, 0.1)
        L = rng.uniform(55, 85)
        droop = rng.uniform(0.35, 0.6)
        side_a, side_b = [], []
        for i in range(13):
            u = i / 12
            cx = top[0] + math.cos(th) * L * u
            cy = top[1] + math.sin(th) * L * u + droop * L * u * u
            wdt = 9 * math.sin(math.pi * u)
            nx, ny = -math.sin(th), math.cos(th)
            side_a.append(((cx + nx * wdt) * SS, (cy + ny * wdt) * SS))
            side_b.append(((cx - nx * wdt) * SS, (cy - ny * wdt) * SS))
        d.polygon(side_a + side_b[::-1], fill=col)
        th2 = math.pi - th + math.pi
        side_a, side_b = [], []
        for i in range(13):
            u = i / 12
            cx = top[0] + math.cos(th2) * L * u
            cy = top[1] + math.sin(th2) * L * u + droop * L * u * u
            wdt = 9 * math.sin(math.pi * u)
            nx, ny = -math.sin(th2), math.cos(th2)
            side_a.append(((cx + nx * wdt) * SS, (cy + ny * wdt) * SS))
            side_b.append(((cx - nx * wdt) * SS, (cy - ny * wdt) * SS))
        d.polygon(side_a + side_b[::-1], fill=col)


@lru_cache(None)
def jungle(seed, col, base, hmin, hmax, width=W + 360, palms=0.25, gap=(34, 70), trunks=False):
    """Camada de mata: copas em cachos de círculos, algumas palmeiras, corpo sólido até o chão."""
    rng = random.Random(seed)
    im = Image.new("RGBA", (width * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hi = mix(col, (200, 230, 160), 0.13) + (255,)
    lo = col + (255,)
    d.rectangle([0, int((base - hmin * 0.35) * SS), width * SS, H * SS], fill=lo)
    x = -30.0
    while x < width + 30:
        h = rng.uniform(hmin, hmax)
        if rng.random() < palms:
            palm(d, x, base - hmin * 0.3, h, lo, rng, rng.uniform(-25, 25))
        else:
            if trunks:
                d.rectangle([(x - 5) * SS, (base - h) * SS, (x + 5) * SS, base * SS], fill=lo)
            for _ in range(rng.randint(4, 7)):
                r = rng.uniform(24, 52)
                cx = x + rng.uniform(-30, 30)
                cy = base - h + rng.uniform(0, h * 0.55)
                d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=lo)
            for _ in range(3):
                r = rng.uniform(12, 24)
                cx = x + rng.uniform(-26, 18)
                cy = base - h + rng.uniform(-6, h * 0.25)
                d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=hi)
        x += rng.uniform(*gap)
    return im


@lru_cache(None)
def ferns(seed, col, width=W + 200):
    """Folhagem do primeiro plano, nos cantos de baixo."""
    rng = random.Random(seed)
    im = Image.new("RGBA", (width * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx0, n in [(-20, 9), (width + 20, 9)]:
        for _ in range(n):
            bx = cx0 + rng.uniform(-40, 40)
            th = math.radians(rng.uniform(-80, -20) if cx0 < 0 else rng.uniform(-160, -100))
            L = rng.uniform(140, 260)
            side_a, side_b = [], []
            for i in range(15):
                u = i / 14
                px = bx + math.cos(th) * L * u
                py = H + 10 + math.sin(th) * L * u + 0.5 * L * u * u
                wdt = 22 * math.sin(math.pi * u ** 0.8)
                side_a.append(((px - wdt * math.sin(th)) * SS, (py + wdt * math.cos(th)) * SS))
                side_b.append(((px + wdt * math.sin(th)) * SS, (py - wdt * math.cos(th)) * SS))
            d.polygon(side_a + side_b[::-1], fill=col + (255,))
    return im


FAR = ((52, 118, 92), 430, 120, 190)
MID = ((30, 88, 58), 480, 110, 200)


def forest_back(cv, t, pan=0.0, smoke=0.0):
    cv.paste(jungle(1, *FAR, palms=0.15), -120 - pan * 0.4)
    if smoke > 0:
        smoke_plume(cv, t, 190, 330, smoke)
    cv.paste(jungle(2, *MID, palms=0.3), -150 - pan * 0.8)


def smoke_plume(cv, t, x, y, a):
    for i in range(14):
        u = ((t * 0.18) + i / 14) % 1.0
        r = 18 + 70 * u
        px = x + 40 * u + math.sin(u * 7 + i) * 14
        py = y - 230 * u
        cv.circ((px, py), r, (110, 104, 100), a * 0.55 * (1 - u) * min(1, u * 6))
    cv.glow((x, y + 40), 90, (255, 110, 40), a * 0.8)


# ---------------------------------------------------------------- elementos

def limb(cv, p0, ang_up, ang_fore, s, side, sleeve=None, w=11, skin=SKIN):
    """Braço em dois segmentos; ângulos em graus a partir da vertical para baixo, positivo para fora."""
    sg = -1 if side == "L" else 1
    a1, a2 = math.radians(ang_up), math.radians(ang_fore)
    e = (p0[0] + sg * math.sin(a1) * 36 * s, p0[1] + math.cos(a1) * 36 * s)
    h = (e[0] + sg * math.sin(a2) * 33 * s, e[1] + math.cos(a2) * 33 * s)
    cv.line([p0, e, h], skin, w * s)
    if sleeve:
        cv.line([p0, lerp(p0, e, 0.4)], sleeve, (w + 4) * s)
    cv.circ(h, 6.5 * s, skin)
    return h


def person(cv, x, y, s, t=0.0, walk=0.0, arms=((12, 8), (12, 8)), look=0.0, shirt=SHIRT, hair=HAIR,
           paint=True, a=1.0, seed=0, mouth="smile", shorts=SHORTS, necklace=True, skin=SKIN):
    """Personagem de frente com os pés em (x, y). Altura ~ 250*s."""
    if a <= 0.01:
        return {"L": (x - 40 * s, y - 110 * s), "R": (x + 40 * s, y - 110 * s)}
    ph = t * 2 * math.pi * 1.7
    bob = 3 * s * abs(math.sin(ph)) * walk
    y = y - bob
    for side, sg in (("L", -1), ("R", 1)):
        sw = math.sin(ph) * sg * walk
        lift = max(0.0, math.cos(ph) * sg) * 7 * s * walk
        hip = (x + sg * 11 * s, y - 95 * s + bob)
        foot = (x + sg * 13 * s + sw * 8 * s, y - lift + bob)
        cv.line([hip, foot], skin, 15 * s)
        cv.ell((foot[0] + sg * 3 * s, foot[1] - 2 * s), 10 * s, 5 * s, (90, 60, 40))
    cv.poly([(x - 28 * s, y - 124 * s), (x + 28 * s, y - 124 * s), (x + 30 * s, y - 80 * s), (x + 3 * s, y - 80 * s),
             (x, y - 96 * s), (x - 3 * s, y - 80 * s), (x - 30 * s, y - 80 * s)], shorts)
    cv.rect((x - 9 * s, y - 202 * s, x + 9 * s, y - 182 * s), skin)
    cv.poly([(x - 31 * s, y - 186 * s), (x + 31 * s, y - 186 * s), (x + 28 * s, y - 118 * s), (x - 28 * s, y - 118 * s)], shirt)
    cv.circ((x - 28 * s, y - 180 * s), 9 * s, shirt)
    cv.circ((x + 28 * s, y - 180 * s), 9 * s, shirt)
    cv.poly([(x - 10 * s, y - 186 * s), (x + 10 * s, y - 186 * s), (x, y - 176 * s)], skin)
    if necklace:
        for i in range(9):
            th = math.radians(25 + i * 16.25)
            cv.circ((x + 19 * s * math.cos(th), y - 190 * s + 11 * s * math.sin(th)), 2.7 * s,
                    URUCUM if i % 2 else (40, 30, 26))
    hands = {}
    hands["L"] = limb(cv, (x - 30 * s, y - 180 * s), arms[0][0], arms[0][1], s, "L", sleeve=shirt, skin=skin)
    hands["R"] = limb(cv, (x + 30 * s, y - 180 * s), arms[1][0], arms[1][1], s, "R", sleeve=shirt, skin=skin)
    head(cv, x, y - 224 * s, s, t, look, hair, paint, seed, mouth, skin)
    return hands


def head(cv, x, hy, s, t=0.0, look=0.0, hair=HAIR, paint=True, seed=0, mouth="smile", skin=SKIN):
    hc = (x, hy)
    cv.circ((x - 26 * s, hc[1] + 4 * s), 6 * s, skin)
    cv.circ((x + 26 * s, hc[1] + 4 * s), 6 * s, skin)
    cv.circ(hc, 27 * s, skin)
    # cabelo liso com franja reta
    top = [(x + 30 * s * math.cos(math.radians(d)), hc[1] - 2 * s + 31 * s * math.sin(math.radians(d)))
           for d in range(180, 361, 10)]
    cv.poly(top + [(x + 30 * s, hc[1] - 6 * s), (x - 30 * s, hc[1] - 6 * s)], hair)
    cv.rect((x - 30 * s, hc[1] - 10 * s, x - 23 * s, hc[1] + 12 * s), hair)
    cv.rect((x + 23 * s, hc[1] - 10 * s, x + 30 * s, hc[1] + 12 * s), hair)
    ex = look * 4 * s
    blink = ((t + seed * 1.7) % 4.3) < 0.12
    for sg in (-1, 1):
        if blink:
            cv.line([(x + sg * 10 * s + ex - 3.5 * s, hc[1] + 4 * s), (x + sg * 10 * s + ex + 3.5 * s, hc[1] + 4 * s)],
                    (30, 20, 16), 1.8 * s)
        else:
            cv.circ((x + sg * 10 * s + ex, hc[1] + 4 * s), 3.3 * s, (30, 20, 16))
        if paint:
            for dy in (12, 16.5):
                cv.line([(x + sg * 11 * s, hc[1] + dy * s), (x + sg * 21 * s, hc[1] + dy * s)], URUCUM, 2.5 * s)
    if mouth == "smile":
        cv.arc((x + ex * 0.5, hc[1] + 12 * s), 7 * s, 25, 155, (90, 40, 30), 2.0 * s)
    elif mouth == "worry":
        cv.arc((x + ex * 0.5, hc[1] + 22 * s), 6 * s, 210, 330, (90, 40, 30), 2.0 * s)
    else:
        cv.circ((x + ex * 0.5, hc[1] + 17 * s), 3.2 * s, (90, 40, 30))


def oca(cv, cx, base, w, h, solar=0.0):
    pts = [(cx + w / 2 * math.cos(math.radians(d)), base - h * math.sin(math.radians(d))) for d in range(0, 181, 6)]
    cv.poly(pts, STRAW)
    for k in (0.82, 0.62, 0.42):
        cv.line([(cx + w / 2 * k * math.cos(math.radians(d)) * 1.08, base - h * (1 - (1 - k) * 0.25)
                  * math.sin(math.radians(d)) * k ** 0.25) for d in range(8, 173, 8)], dim(STRAW, 0.78), 2.2)
    cv.poly([(cx - 8, base - h + 2), (cx + 8, base - h + 2), (cx, base - h - 18)], dim(STRAW, 0.8))
    door = [(cx + w * 0.09 * math.cos(math.radians(d)), base - h * 0.42 * math.sin(math.radians(d))) for d in range(0, 181, 15)]
    cv.poly(door, (54, 36, 22))
    if solar > 0:
        k = ease(solar)
        px, py = cx + w * 0.17, base - h * 0.78
        q = [(px - 30 * k, py + 4), (px + 30 * k, py - 12), (px + 36 * k, py + 6), (px - 24 * k, py + 22)]
        cv.poly(q, PANEL)
        cv.line([q[0], q[1]], (180, 210, 240), 1.2, 0.6)
        cv.line([lerp(q[0], q[3], 0.5), lerp(q[1], q[2], 0.5)], (180, 210, 240), 1.0, 0.6)
        cv.line([lerp(q[0], q[1], 0.5), lerp(q[3], q[2], 0.5)], (180, 210, 240), 1.0, 0.6)


def door_glow(cv, cx, base, w, h, a):
    if a > 0:
        cv.glow((cx, base - h * 0.2), w * 0.45, (255, 170, 80), a)
        door = [(cx + w * 0.09 * math.cos(math.radians(d)), base - h * 0.42 * math.sin(math.radians(d))) for d in range(0, 181, 15)]
        cv.poly(door, (255, 168, 80), a * 0.85)


def dish(cv, x, base, k, a=1.0):
    """Antena de satélite plana num mastro; k = 0..1 montagem."""
    hgt = 128 * ease(prog(k, 0.0, 0.5))
    if hgt <= 1:
        return None
    cv.line([(x, base), (x, base - hgt)], (130, 136, 140), 5, a)
    cv.line([(x - 16, base), (x, base - 28)], (130, 136, 140), 3, a)
    cv.line([(x + 16, base), (x, base - 28)], (130, 136, 140), 3, a)
    top = (x, base - hgt)
    kd = ease(prog(k, 0.45, 1.0))
    if kd <= 0:
        return top
    ang = math.radians(-28)
    wv, hv = 40 * kd, 26 * kd
    ux, uy = math.cos(ang), math.sin(ang)
    vx, vy = -uy * 0.55, ux * 0.55
    c = (top[0] + 4, top[1] - 12)
    q = [(c[0] - ux * wv - vx * hv, c[1] - uy * wv - vy * hv), (c[0] + ux * wv - vx * hv, c[1] + uy * wv - vy * hv),
         (c[0] + ux * wv + vx * hv, c[1] + uy * wv + vy * hv), (c[0] - ux * wv + vx * hv, c[1] - uy * wv + vy * hv)]
    cv.line([top, c], (150, 154, 158), 4, a)
    cv.poly(q, (238, 240, 242), a, outline=(150, 156, 160), w=1.5)
    return c


def satellite(cv, p, a, s=1.0):
    x, y = p
    cv.rect((x - 3 * s, y - 2.5 * s, x + 3 * s, y + 2.5 * s), (230, 232, 236), a)
    cv.rect((x - 13 * s, y - 2 * s, x - 5 * s, y + 2 * s), (90, 130, 200), a)
    cv.rect((x + 5 * s, y - 2 * s, x + 13 * s, y + 2 * s), (90, 130, 200), a)


@lru_cache(None)
def stars(seed=7, n=150):
    rng = random.Random(seed)
    return [(rng.uniform(0, W), rng.uniform(0, 330), rng.uniform(0.6, 1.8), rng.uniform(0, 6.28)) for _ in range(n)]


def draw_stars(cv, t, a):
    if a <= 0.01:
        return
    for x, y, r, ph in stars():
        cv.circ((x, y), r, (230, 236, 255), a * (0.55 + 0.45 * math.sin(t * 2 + ph)))


def laptop_front(cv, cx, cy, wd, open_k, glow_a=0.0, back=True):
    """Notebook visto de frente: base e tampa; com back=True vemos a parte de trás da tampa."""
    hb = 10
    cv.rect((cx - wd / 2 - 6, cy, cx + wd / 2 + 6, cy + hb), (150, 156, 164), r=3)
    hl = wd * 0.66 * open_k
    if hl < 2:
        return
    if back:
        cv.rect((cx - wd / 2, cy - hl, cx + wd / 2, cy), (176, 182, 190), r=6)
        logo(cv, cx, cy - hl / 2, min(28, hl * 0.4), 1.0, 0.8 * open_k, c=(120, 128, 136))
    else:
        cv.rect((cx - wd / 2, cy - hl, cx + wd / 2, cy), (40, 44, 50), r=6)
        cv.rect((cx - wd / 2 + 6, cy - hl + 6, cx + wd / 2 - 6, cy - 6), mix((20, 30, 34), GREEN, 0.25 * glow_a), r=3)


def phone_card(cv, x, y, wd, hgt, a, glow_c=GREEN):
    cv.rect((x - wd / 2, y - hgt / 2, x + wd / 2, y + hgt / 2), (26, 30, 36), a, r=14, outline=(200, 206, 214), w=2)


def warn_icon(cv, p, s, c, a):
    x, y = p
    cv.poly([(x, y - 12 * s), (x + 13 * s, y + 10 * s), (x - 13 * s, y + 10 * s)], c, a)
    cv.text((x, y + 2 * s), "!", "bold", int(16 * s), INK, a)


def wifi(cv, p, t, a, rmax=380, c=GREEN, speed=0.5, n=4):
    for i in range(n):
        u = (t * speed + i / n) % 1.0
        r = 30 + rmax * u
        cv.arc(p, r, 200, 340, c, 3.0, a * (1 - u) ** 1.3)


# ---------------------------------------------------------------- cenas

def scene_intro(cv, t, L):
    cv.im.paste(sky_at(2), (0, 0))
    draw_stars(cv, t, 0.9)
    cv.paste(jungle(1, *FAR, palms=0.15), -120)
    cv.paste(jungle(2, *MID, palms=0.3), -150)
    cv.shade((4, 8, 22), 0.68)
    rng = random.Random(3)
    for i in range(26):
        bx, by, sp = rng.uniform(0, W), rng.uniform(380, 660), rng.uniform(0.3, 0.8)
        x = bx + math.sin(t * sp + i) * 30
        y = by + math.cos(t * sp * 1.3 + i) * 16
        a = 0.5 + 0.5 * math.sin(t * 3 + i * 2)
        cv.glow((x, y), 14, (220, 255, 120), a)
        cv.circ((x, y), 2, (240, 255, 170), a)
    cv.paste(ferns(5, (6, 26, 16)), -100)
    a = env(t, 0, T_ALDEIA, 0.5, 0.8)
    logo(cv, W / 2, 128, 60, prog(t, 0.4, 2.0), a)
    cv.text((W / 2, 196), L["pre"], "bold", 20, GRAY, a * ease(prog(t, 1.0, 1.8)))
    k = ease(prog(t, 1.8, 2.8))
    cv.text((W / 2, 300 + (1 - k) * 14), "Kauã", "russo", 118, WHITE, a * k)
    k2 = ease(prog(t, 2.5, 3.4))
    cv.text((W / 2, 392), L["sub"], "semi", 44, GREEN, a * k2)
    k3 = ease(prog(t, 3.3, 4.2))
    cv.text((W / 2, 456), L["tag"], "med", 24, AMBER, a * k3)


GROUND = 548
OCAS = [(1090, GROUND + 4, 190, 132), (870, GROUND, 240, 168), (668, GROUND + 6, 150, 104)]
DISH_X = 560


def aldeia_ground(cv, t):
    cv.poly([(0, GROUND - 14), (W, GROUND - 22), (W, H), (0, H)], SOIL)
    cv.poly([(0, GROUND - 14), (W, GROUND - 22), (W, GROUND - 8), (0, GROUND)], dim(SOIL, 0.82))
    cv.poly([(0, 648), (W, 636), (W, H), (0, H)], WATER)
    for i in range(9):
        x = (i * 157 + t * 22) % (W + 120) - 60
        cv.line([(x, 668 + (i % 3) * 14), (x + 46, 668 + (i % 3) * 14)], (150, 200, 220), 2, 0.55)


def scene_aldeia(cv, t, L):
    """Mata e aldeia: amanhecer, perigo, antena, satélites e conexão (8 a 50 s)."""
    nk = 2 * ease(prog(t, 30.5, 38.0))          # 0 dia -> 2 noite
    pan = 60 * ease(prog(t, 8, 30))
    cv.im.paste(sky_at(nk), (0, 0))
    sun_y = 250 + 200 * ease(prog(t, 29, 36))
    if nk < 1.6:
        cv.glow((330 - pan * 0.2, sun_y), 160, (255, 220, 150), 1 - nk / 1.6)
        cv.circ((330 - pan * 0.2, sun_y), 34, (255, 236, 190), 1 - nk / 1.6)
    draw_stars(cv, t, clamp(nk - 1.2) * 1.2)
    smoke = bump(t, 18.6, 30.5, 1.2, 1.5)
    forest_back(cv, t, pan, smoke)
    # pássaros
    if t < 30:
        for i in range(5):
            u = ((t - 8) * 0.06 + i * 0.07) % 1.2
            bx, by = -40 + u * (W + 80), 150 + i * 18 + math.sin(t + i) * 6
            fl = math.sin(t * 9 + i) * 6
            cv.line([(bx - 9, by - fl), (bx, by), (bx + 9, by - fl)], (40, 40, 50), 2.2, 0.8)
    aldeia_ground(cv, t)
    for i, (cx, b, w, h) in enumerate(OCAS):
        oca(cv, cx, b, w, h)
    # antena
    kd = prog(t, 31.0, 34.5)
    dish_c = None
    if t > 30.8:
        dish_c = dish(cv, DISH_X, GROUND + 2, kd)
    # Kauã
    kx = lerp((-60, 0), (430, 0), ease(prog(t, 8.6, 15.5)))[0]
    walking = 1.0 if 8.6 < t < 15.5 else 0.0
    look, arms, mouth = 0.0, ((12, 8), (12, 8)), "smile"
    if 19.5 < t < 24.2:
        look, mouth = -1.0, "worry"
        arms = ((12, 8), (70, 95)) if t < 22.5 else ((12, 8), (12, 8))
        arms = ((80 + 10 * ease(prog(t, 19.5, 20.2)), 95), (12, 8)) if t < 22.5 else arms
    if 24.2 < t < 30.5:
        mouth = "worry"
        arms = ((12, 8), (40, 140))
    if 30.5 < t < 36:
        kx = 430 + 40 * ease(prog(t, 30.5, 32))
        arms = ((12, 8), (60, 30))
    if t >= 36:
        kx = 470
        look = 0.6
        mouth = "smile" if t > 42 else "o"
        arms = ((12, 8), (12, 8)) if t < 42 else ((150, 170), (150, 170))
        if t > 42:
            wave = math.sin(t * 6) * 10
            arms = ((140 + wave, 165), (140 - wave, 165))
    hands = person(cv, kx, GROUND + 70, 0.82, t, walk=walking, arms=arms, look=look, mouth=mouth)
    # o ancião ajuda a montar a antena
    ea = bump(t, 30.2, 37.5, 0.8, 0.8)
    if ea > 0:
        person(cv, DISH_X + 80, GROUND + 66, 0.78, t, arms=((12, 8), (55, 40)), shirt=(186, 112, 60),
               hair=(176, 176, 176), paint=False, a=ea, seed=3, necklace=True)
    # crianças ganham conexão
    kc = ease(prog(t, 43.0, 44.2))
    if kc > 0:
        for j, (cxk, sh) in enumerate([(760, (236, 120, 60)), (990, (80, 150, 220)), (1180, (230, 200, 70))]):
            hk = person(cv, cxk, GROUND + 92, 0.5, t + j, arms=((20, 150), (20, 150)), shirt=sh, a=kc, seed=j + 5)
            hc = lerp(hk["L"], hk["R"], 0.5)
            cv.rect((hc[0] - 7, hc[1] - 14, hc[0] + 7, hc[1] + 4), (24, 28, 34), kc, r=2)
    # véu de noite
    cv.shade((6, 12, 40), 0.5 * clamp(nk - 0.6) / 1.4 * 1.4 if nk > 0.6 else 0)
    for (cx, b, w, h) in OCAS:
        door_glow(cv, cx, b, w, h, clamp(nk - 1.2))
    cv.paste(ferns(5, dim((10, 40, 24), 1 - 0.35 * clamp(nk - 0.6))), -100)
    # satélites e feixe
    if t > 35.5:
        ka = ease(prog(t, 35.5, 37.0))
        sats = []
        for i in range(10):
            u = (t - 35.5) * 0.045 + i * 0.085 - 0.2
            sx = -60 + u * (W + 120)
            sy = 70 + 60 * math.sin(u * 2.2) + i * 4
            if -40 < sx < W + 40:
                sats.append((sx, sy))
                satellite(cv, (sx, sy), ka * 0.95)
                cv.glow((sx, sy), 14, (200, 220, 255), ka * 0.5)
        if dish_c and sats and t > 37.5:
            sp = min(sats, key=lambda q: abs(q[0] - dish_c[0] - 120))
            kb = ease(prog(t, 37.5, 38.5))
            cv.line([dish_c, sp], GREEN, 2.0, kb * 0.65)
            for j in range(5):
                u = ((t * 0.9) + j / 5) % 1.0
                cv.circ(lerp(sp, dish_c, u), 3.2, (180, 255, 210), kb)
            cv.glow(dish_c, 40, GREEN, kb)
        if dish_c and t > 41.5:
            kw = ease(prog(t, 41.5, 42.5))
            wifi(cv, (dish_c[0], dish_c[1] + 10), t, kw * 0.9, rmax=520)
    if 42.4 < t < 50:
        k = bump(t, 42.4, 50, 0.4, 0.5)
        cv.rect((DISH_X - 58, 226, DISH_X + 58, 258), (6, 30, 20), k, r=16, outline=GREEN, w=2)
        cv.text((DISH_X, 242), "ONLINE", "bold", 20, GREEN, k)
    # sem sinal / motosserra
    if 19.0 < t < 24.6:
        k = bump(t, 19.0, 24.6, 0.3, 0.4)
        j = math.sin(t * 60) * 2
        cv.text((250 + j, 260), "VRRRR", "russo", 40, RED, k)
    if 24.6 < t < 30.6:
        k = bump(t, 24.6, 30.6, 0.4, 0.4)
        hx, hy = hands["R"]
        cv.rect((hx - 9, hy - 20, hx + 9, hy + 6), (24, 28, 34), k, r=3)
        bx, by = kx + 70, GROUND - 200
        cv.rect((bx - 64, by - 40, bx + 64, by + 30), (250, 250, 250), k * 0.92, r=14)
        for i in range(4):
            cv.rect((bx - 38 + i * 16, by + 6 - i * 10, bx - 28 + i * 16, by + 14), (160, 166, 172), k)
        cv.line([(bx + 26, by - 26), (bx + 48, by - 4)], RED, 4, k)
        cv.line([(bx + 48, by - 26), (bx + 26, by - 4)], RED, 4, k)
        cv.text((bx, by + 50), L["nosignal"], "bold", 20, WHITE, k)
    caption(cv, t, 9.2, 14.0, L["c1"])
    caption(cv, t, 14.3, 18.6, L["c2"])
    caption(cv, t, 18.9, 24.2, L["c3"])
    caption(cv, t, 24.5, 30.2, L["c4"])
    caption(cv, t, 30.6, 36.0, L["c5"])
    caption(cv, t, 36.3, 41.8, L["c6"])
    caption(cv, t, 42.2, 49.6, L["c7"])


def scene_note(cv, t, L):
    """O notebook chega (50 a 64 s)."""
    cv.im.paste(sky("night"), (0, 0))
    draw_stars(cv, t, 0.7)
    cv.paste(jungle(1, *FAR, palms=0.15), -220)
    cv.paste(jungle(2, *MID, palms=0.3), -260)
    cv.poly([(0, 520), (W, 512), (W, H), (0, H)], SOIL)
    oca(cv, 1060, 530, 300, 200)
    cv.shade((6, 12, 40), 0.5)
    door_glow(cv, 1060, 530, 300, 200, 0.8)
    # fogueira
    fx, fy = 250, 600
    cv.glow((fx, fy - 30), 160, (255, 140, 50), 0.9)
    for i in range(3):
        cv.line([(fx - 40 + i * 10, fy + 8), (fx + 30 - i * 10, fy - 4)], (90, 56, 30), 7)
    for i in range(5):
        fl = 22 + 10 * math.sin(t * 9 + i * 1.7)
        xx = fx - 20 + i * 10
        cv.poly([(xx - 9, fy), (xx + 9, fy), (xx + math.sin(t * 6 + i) * 4, fy - fl - 10)],
                mix((255, 120, 40), (255, 220, 90), (i % 2) * 0.6), 0.9)
    kx, ky, s = 640, 676, 1.25
    open_k = ease(prog(t, 52.6, 54.0))
    on = ease(prog(t, 53.6, 54.6))
    seated = t > 55.0
    kb = ease(prog(t, 50.4, 51.4))
    if not seated:
        hands = person(cv, kx, ky, s, t, arms=((40, 100), (40, 100)) if t > 51.6 else ((12, 8), (12, 8)),
                       mouth="o" if t > 52.6 else "smile", look=0.0)
        # caixa
        bx, by = kx, 560
        lid = ease(prog(t, 51.6, 52.6))
        cv.rect((bx - 90, by - 50, bx + 90, by + 50), (176, 128, 74), kb, r=4)
        cv.poly([(bx - 90, by - 50), (bx - 90 - 40 * lid, by - 50 - 46 * lid), (bx - 6, by - 50 - 46 * lid), (bx, by - 50)],
                (196, 146, 88), kb)
        cv.poly([(bx + 90, by - 50), (bx + 90 + 40 * lid, by - 50 - 46 * lid), (bx + 6, by - 50 - 46 * lid), (bx, by - 50)],
                (196, 146, 88), kb)
        cv.text((bx, by + 6), L["box"], "bold", 18, (70, 44, 20), kb)
        cv.circ((bx, by - 22), 9, URUCUM, kb)
        rise = ease(prog(t, 52.0, 53.2))
        if rise > 0:
            ly = by - 50 - 60 * rise
            laptop_front(cv, bx, ly, 150, open_k, on, back=False)
            if on > 0:
                cv.glow((bx, ly - 50), 220, (150, 255, 200), on * 0.8)
    else:
        ks = ease(prog(t, 55.0, 55.8))
        typing = math.sin(t * 14) * 4
        person(cv, kx, 650, s, t, arms=((22, 60 + typing), (22, 60 - typing)), look=0.0, mouth="smile")
        cv.rect((kx - 160, 604, kx + 160, 704), (96, 62, 36), 1, r=18)
        cv.rect((kx - 160, 604, kx + 160, 620), (122, 82, 50), 1, r=8)
        laptop_front(cv, kx, 590, 150, 1.0, 1.0, back=True)
        cv.glow((kx, 400), 170, (150, 255, 210), 0.55 * ks)
        cv.circ((kx, 370), 36, (190, 255, 220), 0.08 * ks)
    caption(cv, t, 50.6, 55.4, L["c8"])
    caption(cv, t, 55.7, 63.6, L["c9"])


def bubble(cv, x, y, wd, s, f, size, me, a, reveal=1.0):
    """Balão de chat com quebra de linha; devolve a altura."""
    lines = wrap(s, f, size, wd - 36)
    lh = size * 1.32
    hgt = len(lines) * lh + 24
    col = (30, 70, 52) if me else (36, 40, 46)
    edge = GREEN if me else (226, 132, 88)
    x0 = x + (W * 0 if not me else 0)
    cv.text_box((x0, y, x0 + wd, y + hgt), col, a, r=14, outline=edge, w=1)
    total = sum(len(l) for l in lines)
    nshow = int(total * reveal + 0.5)
    for i, l in enumerate(lines):
        part = l[:max(0, nshow)]
        nshow -= len(l)
        if part:
            cv.text((x0 + 18, y + 12 + lh * (i + 0.5)), part, f, size, WHITE, a, anchor="lm")
    return hgt


CODE = [
    ("import", "audio, modelo, alerta"),
    ("", ""),
    ("sons", "= audio.gravar(mata, horas=48)"),
    ("rede", "= modelo.treinar(sons, classes)"),
    ("", ""),
    ("while", "sensor.ligado:"),
    ("   som", "= sensor.escutar(seg=2)"),
    ("   p", "= rede.prever(som)"),
    ("   if", "p['motosserra'] > 0.9:"),
    ("      alerta", ".aldeia(sensor.local)"),
]


def scene_ia(cv, t, L):
    """Tela do notebook com o chat com o Claude (64 a 96 s)."""
    cv.im.paste(gradient((14, 20, 26), (6, 10, 14)), (0, 0))
    sx0, sy0, sx1, sy1 = 70, 34, 1210, 600
    cv.rect((sx0 - 14, sy0 - 14, sx1 + 14, sy1 + 14), (54, 58, 64), r=22)
    cv.rect((sx0, sy0, sx1, sy1), (22, 25, 30), r=8)
    cv.rect((sx0, sy0, sx1, sy0 + 46), (32, 36, 42), r=8)
    for i, c in enumerate([(236, 96, 86), (240, 190, 70), (90, 200, 110)]):
        cv.circ((sx0 + 24 + i * 22, sy0 + 23), 6, c)
    cv.circ((sx0 + 120, sy0 + 23), 9, (226, 132, 88))
    cv.text((sx0 + 138, sy0 + 23), "Claude", "bold", 21, WHITE, anchor="lm")
    # a câmera mostra o rosto do Kauã, no canto
    cv.circ((sx1 - 50, sy0 + 23), 19, (40, 70, 60))
    head(cv, sx1 - 50, sy0 + 21, 0.52, t)
    split = ease(prog(t, 84.0, 85.5))
    chat_w = 1040 - 470 * split
    cx0 = sx0 + 30
    # campo de digitação
    cv.rect((cx0, sy1 - 62, cx0 + chat_w, sy1 - 18), (34, 38, 44), r=20, outline=(70, 76, 84), w=1)
    cv.text((cx0 + 22, sy1 - 40), L["placeholder"], "med", 18, GRAY, anchor="lm")
    msgs = [("u1", 64.8, True), ("a1", 68.6, False), ("u2", 76.6, True), ("a2", 79.4, False)]
    y = sy0 + 64
    fsize = 19 if split < 0.5 else 17
    shown = [m for m in msgs if t > m[1]]
    # rola para cima quando não cabe
    heights = []
    for key, t0, me in shown:
        heights.append(len(wrap(L[key], "med", fsize, (chat_w * (0.78 if me else 0.9)) - 36)) * fsize * 1.32 + 24 + 14)
    over = sum(heights) - (sy1 - 84 - (sy0 + 64))
    y -= max(0, over)
    for (key, t0, me), hh in zip(shown, heights):
        wd = chat_w * (0.78 if me else 0.9)
        speed = 38 if me else 70
        rev = clamp((t - t0) * speed / max(1, len(L[key])))
        a = ease(prog(t, t0, t0 + 0.3))
        x = cx0 + chat_w - wd if me else cx0
        if y + hh > sy0 + 50:
            bubble(cv, x, y, wd, L[key], "med", fsize, me, a, rev)
        y += hh
    # painel direito: código e teste do modelo
    if split > 0:
        px0 = cx0 + chat_w + 24
        px1 = sx1 - 26
        a = split
        cv.rect((px0, sy0 + 62, px1, sy0 + 300), (16, 19, 23), a, r=10, outline=(60, 66, 74), w=1)
        cv.text((px0 + 16, sy0 + 82), "kaa_sentinela.py", "bold", 16, GRAY, a, anchor="lm")
        nl = int((t - 85.0) * 4)
        for i, (kw, rest) in enumerate(CODE[:max(0, nl)]):
            yy = sy0 + 110 + i * 19
            cv.text((px0 + 16, yy), kw, "semi", 15, (226, 132, 88) if kw.strip() in ("import", "while", "if") else GREEN, a, anchor="lm")
            cv.text((px0 + 16 + font("semi", 15).getlength(kw + " "), yy), rest, "med", 15, WHITE, a, anchor="lm")
        ty = sy0 + 318
        kt = ease(prog(t, 88.0, 89.0))
        cv.rect((px0, ty, px1, sy1 - 18), (16, 19, 23), kt, r=10, outline=(60, 66, 74), w=1)
        cv.text((px0 + 16, ty + 20), L["test"], "bold", 16, GRAY, kt, anchor="lm")
        # forma de onda
        wx0, wx1, wy = px0 + 16, px1 - 16, ty + 62
        pts = []
        for i in range(120):
            u = i / 119
            v = math.sin(u * 90 + t * 20) * (0.5 + 0.5 * math.sin(u * 7 + t)) * 18
            pts.append((wx0 + (wx1 - wx0) * u, wy + v))
        cv.line(pts, AMBER, 1.6, kt)
        vals = [0.97, 0.01, 0.01, 0.01]
        kb = ease(prog(t, 89.5, 91.5))
        for i, (nm, v) in enumerate(zip(L["classes"], vals)):
            yy = ty + 108 + i * 30
            cv.text((px0 + 16, yy), nm, "med", 16, WHITE, kt, anchor="lm")
            bx0 = px0 + 150
            cv.rect((bx0, yy - 7, px1 - 70, yy + 7), (40, 44, 50), kt, r=7)
            cv.rect((bx0, yy - 7, bx0 + max(14, (px1 - 70 - bx0) * v * kb), yy + 7), RED if i == 0 else GRAY, kt, r=7)
            cv.text((px1 - 20, yy), f"{v * kb * 100:.0f}%", "bold", 16, RED if i == 0 else GRAY, kt, anchor="rm")
    caption(cv, t, 64.6, 70.6, L["c10"], y=660)
    caption(cv, t, 71.0, 77.8, L["c11"], y=660)
    caption(cv, t, 78.2, 86.6, L["c12"], y=660)
    caption(cv, t, 87.0, 95.6, L["c13"], y=660)


TRUNKS = [(250, 34), (530, 40), (800, 46), (1070, 38)]


def sensor(cv, x, y, a, alarm=0.0, t=0.0):
    cv.rect((x - 26, y - 46, x + 26, y - 22), PANEL, a, r=2)
    cv.line([(x - 26, y - 34), (x + 26, y - 34)], (170, 200, 240), 1, a * 0.6)
    cv.rect((x - 12, y - 18, x + 12, y + 22), (26, 30, 36), a, r=4)
    c = mix(GREEN, RED, alarm)
    cv.rect((x - 8, y - 12, x + 8, y + 14), c, a * 0.9, r=2)
    cv.glow((x, y), 46, c, a * (0.6 + 0.4 * math.sin(t * 6)) * (0.5 + alarm))
    cv.line([(x - 24, y + 4), (x + 24, y + 4)], (70, 50, 30), 4, a)


def scene_kaa(cv, t, L):
    """Kaá Sentinela em ação, à noite (96 a 110 s)."""
    cv.im.paste(sky("night"), (0, 0))
    draw_stars(cv, t, 0.6)
    cv.circ((1040, 110), 36, (240, 240, 220))
    cv.glow((1040, 110), 120, (220, 230, 255), 0.6)
    cv.paste(jungle(11, (28, 70, 60), 420, 140, 220, palms=0.2), -100)
    cv.paste(jungle(12, (18, 50, 38), 500, 120, 220, palms=0.3, trunks=True), -60)
    cv.poly([(0, 560), (W, 556), (W, H), (0, H)], (40, 44, 26))
    cv.shade((6, 12, 40), 0.42)
    for x, w in TRUNKS:
        cv.poly([(x - w / 2, 570), (x + w / 2, 570), (x + w * 0.35, 0), (x - w * 0.35, 0)], (60, 42, 30))
        cv.line([(x - w * 0.1, 560), (x - w * 0.05, 40)], (80, 58, 40), 3)
    # aldeia à esquerda, ao longe
    oca(cv, 110, 572, 150, 100)
    door_glow(cv, 110, 572, 150, 100, 0.9)
    alarm = ease(prog(t, 100.0, 100.6)) * (1 - ease(prog(t, 106.4, 107.4)))
    ks = [ease(prog(t, 96.4 + i * 0.5, 97.0 + i * 0.5)) for i in range(3)]
    sens = [(530, 330), (800, 360), (1070, 320)]
    for i, (x, y) in enumerate(sens):
        sensor(cv, x, y, ks[i], alarm if i == 2 else 0.0, t + i)
        if ks[i] > 0.5 and t < 99.5:
            for j in range(3):
                u = (t * 0.6 + j / 3) % 1.0
                cv.arc((x, y), 30 + 70 * u, 0, 360, GREEN, 1.6, ks[i] * (1 - u) * 0.5)
    # motosserra fora de cena, à direita
    ksaw = bump(t, 98.6, 106.6, 0.4, 0.8)
    if ksaw > 0:
        for j in range(4):
            u = (t * 1.4 + j / 4) % 1.0
            cv.arc((1300, 470), 40 + 220 * u, 150, 230, RED, 3, ksaw * (1 - u))
        cv.text((1180 + math.sin(t * 60) * 2, 430), "VRRRR", "russo", 30, RED, ksaw)
    if alarm > 0:
        x, y = sens[2]
        r = 30 + 60 * ((t * 1.5) % 1.0)
        cv.circ((x, y), r, RED, alarm * (1 - (t * 1.5) % 1.0) * 0.8, w=3)
        cv.text_box((x - 112, y - 104, x + 112, y - 70), (60, 14, 10), alarm * 0.9, r=17, outline=RED, w=2)
        cv.text((x, y - 87), L["detect"], "bold", 19, WHITE, alarm)
        # salto do alerta de sensor em sensor até a aldeia
        path = [sens[2], sens[1], sens[0], (110, 500)]
        kp = ease(prog(t, 100.6, 101.6))
        cv.line(partial(path, kp), AMBER, 2.4, alarm * 0.8)
        if kp >= 1:
            for j in range(4):
                u = ((t * 0.8) + j / 4) % 1.0
                cv.circ(partial(path, u)[-1], 4, (255, 220, 140), alarm)
    ka = bump(t, 101.6, 109.6, 0.4, 0.5)
    if ka > 0:
        ax, ay = 210, 190
        cv.text_box((ax - 150, ay - 62, ax + 150, ay + 62), (24, 28, 34), ka * 0.95, r=18, outline=AMBER, w=2)
        cv.text((ax - 112, ay - 30), "!", "bold", 26, AMBER, ka)
        cv.text((ax - 92, ay - 30), L["alert"], "bold", 22, AMBER, ka, anchor="lm")
        cv.text((ax - 126, ay + 14), L["alert_body"], "semi", 18, WHITE, ka, anchor="lm")
    # guardiões partem com lanternas
    kg = ease(prog(t, 103.2, 108.6))
    if t > 103.0:
        for j, sh in enumerate([SHIRT, (236, 120, 60), (80, 150, 220)]):
            gx = 120 + 640 * kg - j * 70
            hk = person(cv, gx, 690 - j * 6, 0.52, t + j * 0.3, walk=1.0 if kg < 1 else 0.0,
                        arms=((12, 8), (75, 80)), shirt=sh, seed=j)
            hx, hy = hk["R"]
            cv.poly([(hx, hy), (hx + 220, hy - 60), (hx + 220, hy + 40)], (255, 240, 170), 0.12)
    if t > 106.8:
        k = ease(prog(t, 106.8, 107.6)) * (1 - ease(prog(t, 109.4, 110)))
        cv.text_box((W / 2 - 170, 70, W / 2 + 170, 116), (6, 30, 20), k * 0.9, r=22, outline=GREEN, w=2)
        cv.text((W / 2, 93), L["protected"], "bold", 24, GREEN, k)
    kt = bump(t, 96.2, 106.6, 0.5, 0.5)
    cv.text((W / 2, 70), "KAÁ SENTINELA", "russo", 40, GREEN, kt)
    cv.text((W / 2, 112), L["kaa"], "med", 20, AMBER, kt)
    caption(cv, t, 96.6, 102.8, L["c14"])
    caption(cv, t, 103.2, 109.6, L["c15"])


GLOBE = (420, 330, 210)


def scene_mundo(cv, t, L):
    """Sucesso internacional (110 a 128 s)."""
    cv.im.paste(sky("space"), (0, 0))
    draw_stars(cv, t, 0.8)
    gx, gy, R = GLOBE
    cv.glow((gx, gy), R * 1.5, (60, 140, 220), 0.6)
    cv.circ((gx, gy), R, (16, 52, 92))
    rot = (t - 110) * 0.25
    for i in range(6):
        ph = rot + i * math.pi / 6
        rx = abs(math.cos(ph)) * R
        cv.ell((gx, gy), rx, R, (60, 120, 170), 0.5, w=1.2)
    for lat in (-60, -30, 0, 30, 60):
        yy = gy - R * math.sin(math.radians(lat))
        rx = R * math.cos(math.radians(lat))
        cv.ell((gx, yy), rx, rx * 0.12, (60, 120, 170), 0.45, w=1.2)
    # manchas verdes de floresta que crescem
    rng = random.Random(4)
    kgrow = ease(prog(t, 112, 126))
    for i in range(40):
        th = rng.uniform(0, 2 * math.pi)
        rr = R * math.sqrt(rng.uniform(0, 0.85))
        p = (gx + rr * math.cos(th), gy + rr * math.sin(th))
        if rng.random() < kgrow:
            cv.circ(p, rng.uniform(6, 14), (40, 150, 90), 0.6)
    origin = (gx - 40, gy + 70)
    cv.circ(origin, 9, AMBER)
    cv.circ(origin, 9 + 20 * ((t * 0.8) % 1), AMBER, (1 - (t * 0.8) % 1), w=2)
    names = L["countries"]
    for i, nm in enumerate(names):
        k = ease(prog(t, 111.0 + i * 0.7, 112.0 + i * 0.7))
        if k <= 0:
            continue
        ang = math.radians(-150 + i * (300 / (len(names) - 1)))
        p = (gx + (R + 70) * math.cos(ang) * 1.1, gy + (R + 50) * math.sin(ang))
        mid = lerp(origin, p, 0.5)
        mid = (mid[0] + (mid[1] - gy) * 0.3, mid[1] - 60)
        arc = [lerp(lerp(origin, mid, u), lerp(mid, p, u), u) for u in [j / 24 for j in range(25)]]
        cv.line(partial(arc, k), GREEN, 1.6, 0.75)
        if k >= 1:
            cv.circ(p, 5, GREEN)
            cv.text((p[0] + (10 if math.cos(ang) >= 0 else -10), p[1]), nm, "semi", 16, WHITE, 0.9,
                    anchor="lm" if math.cos(ang) >= 0 else "rm")
    # contadores
    rx = 940
    kc = ease(prog(t, 111.0, 112.0))
    u = ease(prog(t, 111.5, 125.5))
    nump = int(round(38 * u))
    numc = int(round(1200 * u))
    money = 12.4 * u ** 1.6
    rows = [(f"{nump}", L["n_paises"], GREEN), (f"{numc:,}".replace(",", "." if L is not TXT["en"] else ","), L["n_com"], GREEN),
            (L["money"](max(money, 0.05)), L["n_rev"], AMBER)]
    for i, (v, lab, c) in enumerate(rows):
        yy = 150 + i * 128
        cv.text((rx, yy), v, "russo", 54 if i < 2 else 40, c, kc)
        cv.text((rx, yy + 46), lab, "med", 20, GRAY, kc)
    # manchetes
    for i, hl in enumerate(HEADLINES):
        t0 = 112.6 + i * 2.3
        k = bump(t, t0, t0 + 2.3, 0.3, 0.3)
        if k <= 0:
            continue
        y = 540 - (1 - eout(prog(t, t0, t0 + 0.4))) * 16
        x = rx
        wd = font("semi", 17).getlength(hl) + 40
        cv.text_box((x - wd / 2, y - 22, x + wd / 2, y + 22), (236, 236, 230), k * 0.95, r=6)
        cv.text((x, y), hl, "semi", 17, INK, k)
    kk = ease(prog(t, 122.0, 123.0))
    if kk > 0:
        person(cv, 1150, 600 + (1 - kk) * 60, 0.62, t, arms=((150, 175), (150, 175)), a=kk)
        for i in range(10):
            u = ((t - 122.0) * 0.5 + i / 10) % 1.0
            px = 1150 + math.sin(i * 2.3) * 120 * u
            py = 420 - 120 * u + 200 * u * u
            cv.circ((px, py), 4, AMBER if i % 2 else GREEN, kk * (1 - u))
    caption(cv, t, 110.5, 116.6, L["c16"])
    caption(cv, t, 117.0, 127.6, L["c17"])


def scene_nova(cv, t, L):
    """A aldeia transformada (128 a 146 s)."""
    cv.im.paste(sky("day"), (0, 0))
    cv.glow((330, 220), 160, (255, 220, 150), 1)
    cv.circ((330, 220), 34, (255, 236, 190))
    forest_back(cv, t, 60)
    aldeia_ground(cv, t)
    up = [ease(prog(t, 129.0 + i * 1.6, 129.8 + i * 1.6)) for i in range(4)]
    for (cx, b, w, h) in OCAS:
        oca(cv, cx, b, w, h, solar=up[0])
    dish(cv, DISH_X, GROUND + 2, 1.0)
    # caixa d'água
    if up[1] > 0:
        x, b = 330, GROUND + 4
        hh = 150 * up[1]
        for sx in (-34, 34):
            cv.line([(x + sx, b), (x + sx * 0.6, b - hh)], (110, 90, 70), 5)
        cv.rect((x - 46, b - hh - 70, x + 46, b - hh), (70, 150, 200), r=10)
        cv.rect((x - 46, b - hh - 70, x + 46, b - hh - 58), (100, 180, 220), r=6)
        cv.circ((x, b - hh - 36), 10, (220, 240, 255), 0.8)
    # posto de saúde
    if up[2] > 0:
        x, b = 150, GROUND + 6
        k = up[2]
        hh = 110 * k
        cv.rect((x - 80, b - hh, x + 80, b), (238, 236, 228))
        cv.poly([(x - 92, b - hh), (x + 92, b - hh), (x, b - hh - 50 * k)], (180, 70, 60))
        cv.rect((x - 18, b - 56 * k, x + 18, b), (90, 120, 150))
        cv.rect((x + 30, b - hh * 0.7 - 10, x + 64, b - hh * 0.7 + 22), (150, 200, 230))
        cv.rect((x - 8, b - hh * 0.8 - 24, x + 8, b - hh * 0.8 + 8), RED)
        cv.rect((x - 16, b - hh * 0.8 - 16, x + 16, b - hh * 0.8), RED)
    # crianças com notebooks (escola conectada)
    ks = up[3]
    if ks > 0:
        cv.rect((640, GROUND + 60, 1040, GROUND + 74), (120, 82, 50), ks, r=4)
        for j, (cxk, sh) in enumerate([(700, (236, 120, 60)), (840, (80, 150, 220)), (980, (230, 200, 70))]):
            typing = math.sin(t * 12 + j) * 4
            person(cv, cxk, GROUND + 112, 0.5, t + j, arms=((24, 70 + typing), (24, 70 - typing)), shirt=sh, a=ks, seed=j + 5)
            laptop_front(cv, cxk, GROUND + 52, 66, 1.0, back=True)
            cv.glow((cxk, GROUND - 20), 60, (150, 255, 210), 0.5 * ks)
        wifi(cv, (DISH_X + 4, GROUND - 136), t, 0.6 * ks, rmax=360)
    person(cv, 470, GROUND + 92, 0.8, t, arms=((12, 8), (110, 150)) if t > 140 else ((12, 8), (12, 8)))
    cv.paste(ferns(5, (10, 40, 24)), -100)
    labels = [(870, GROUND - 210), (330, GROUND - 260), (150, GROUND - 180), (840, GROUND - 95)]
    for i, ((lx, ly), lab) in enumerate(zip(labels, L["up"])):
        k = up[i] * (1 - ease(prog(t, 144.8, 145.8)))
        if k <= 0:
            continue
        wd = font("bold", 18).getlength(lab) + 32
        c = [AMBER, (110, 190, 240), RED, GREEN][i]
        cv.text_box((lx - wd / 2, ly - 18, lx + wd / 2, ly + 18), (10, 14, 18), k * 0.85, r=18, outline=c, w=2)
        cv.text((lx, ly), lab, "bold", 18, WHITE, k)
    caption(cv, t, 128.5, 134.2, L["c18"])
    caption(cv, t, 134.6, 140.2, L["c19"])
    caption(cv, t, 140.6, 145.6, L["c20"])


def icon_dish(cv, x, y, a):
    cv.line([(x, y + 34), (x, y)], GREEN, 4, a)
    cv.poly([(x - 30, y - 6), (x + 22, y - 32), (x + 32, y - 14), (x - 20, y + 12)], GREEN, a * 0.25, outline=GREEN, w=2.5)
    for i in range(3):
        cv.arc((x + 26, y - 30), 14 + i * 10, 250, 340, GREEN, 2.5, a)


def icon_laptop(cv, x, y, a):
    cv.rect((x - 34, y - 34, x + 34, y + 12), None, a, r=4, outline=GREEN, w=2.5)
    cv.rect((x - 44, y + 14, x + 44, y + 22), GREEN, a, r=3)


def icon_ai(cv, x, y, a):
    cv.rect((x - 36, y - 30, x + 36, y + 18), None, a, r=12, outline=GREEN, w=2.5)
    cv.poly([(x - 14, y + 18), (x - 26, y + 34), (x, y + 18)], GREEN, a)
    for i in range(3):
        cv.circ((x - 16 + i * 16, y - 6), 4, GREEN, a)


def scene_moral(cv, t, L):
    """A moral da história (146 a 174 s)."""
    cv.im.paste(gradient((4, 8, 12), (10, 22, 18)), (0, 0))
    cv.paste(jungle(2, (14, 40, 28), 700, 60, 140, palms=0.3), -150)
    a = env(t, T_MORAL, DUR + 1, 0.6, 0.1) * (1 - ease(prog(t, 172.4, 173.8)))
    eq_a = a * (1 - ease(prog(t, 165.4, 166.2)))
    xs = [240, 470, 700, 1000]
    y = 150
    for i, (lab, fn) in enumerate(zip(L["eq"][:3], [icon_dish, icon_laptop, icon_ai])):
        k = ease(prog(t, 146.5 + i * 0.8, 147.3 + i * 0.8)) * eq_a
        fn(cv, xs[i], y - 10, k)
        cv.text((xs[i], y + 52), lab, "semi", 22, WHITE, k)
        sym = "+" if i < 2 else "="
        cv.text(((xs[i] + xs[i + 1]) / 2 - (30 if i == 2 else 0), y), sym, "bold", 44, GRAY, k)
    k = ease(prog(t, 149.0, 150.0)) * eq_a
    cv.glow((xs[3], y), 140, AMBER, k * 0.6)
    cv.text((xs[3], y), L["eq"][3], "russo", 36, AMBER, k)
    for key, t0, t1, c in [("m1", 150.6, 155.6, WHITE), ("m2", 155.8, 160.8, WHITE), ("m3", 161.0, 165.6, AMBER)]:
        k = env(t, t0, t1, 0.5, 0.5) * a
        if k <= 0:
            continue
        lines = wrap(L[key], "semi", 42, 1000)
        lh = 56
        y0 = 390 - (len(lines) - 1) * lh / 2 + (1 - eout(prog(t, t0, t0 + 0.6))) * 12
        for i, l in enumerate(lines):
            cv.text((W / 2, y0 + i * lh), l, "semi", 42, c, k)
    # encerramento
    if t > T_FIM - 0.2:
        k = ease(prog(t, T_FIM, T_FIM + 0.8)) * a
        cv.runs(W / 2, 200, L["end"], "russo", 46, k)
        logo(cv, W / 2, 340, 80, prog(t, T_FIM + 0.6, T_FIM + 2.2), a)
        k2 = ease(prog(t, T_FIM + 1.4, T_FIM + 2.2)) * a
        cv.text((W / 2, 430), "ALEGRETE SUMMIT 2026", "bold", 30, WHITE, k2)
        cv.text((W / 2, 474), L["date"], "semi", 24, GRAY, k2)
        cv.runs(W / 2, 520, L["lema"], "semi", 26, k2)
        cv.text((W / 2, 668), L["fiction"], "med", 18, GRAY, k2)


SCENES = [(0.0, T_ALDEIA, scene_intro), (T_ALDEIA, T_NOTE, scene_aldeia), (T_NOTE, T_IA, scene_note),
          (T_IA, T_KAA, scene_ia), (T_KAA, T_MUNDO, scene_kaa), (T_MUNDO, T_NOVA, scene_mundo),
          (T_NOVA, T_MORAL, scene_nova), (T_MORAL, DUR + 1, scene_moral)]


def draw(t, L):
    cv = Cv()
    for a, b, fn in SCENES:
        if a <= t < b:
            fn(cv, t, L)
            break
    black = 0.0
    for c in CORTES:
        if c == T_FIM:
            continue
        black = max(black, 1 - clamp(abs(t - c) / 0.45))
    black = max(black, 1 - clamp(t / 0.6), ease(prog(t, DUR - 1.2, DUR - 0.1)))
    return cv.render(black)


# ------------------------------------------------------------------ trilha

def intensity(t):
    keys = [(0, 0.1), (8, 0.25), (18, 0.3), (19, 0.15), (30, 0.25), (36, 0.4), (42, 0.75), (50, 0.4), (64, 0.5),
            (85, 0.7), (96, 0.6), (100, 0.75), (110, 0.9), (128, 1.0), (146, 0.7), (166, 0.85), (174, 0.0)]
    xs, ys = zip(*keys)
    return float(np.interp(t, xs, ys))


def _lowpass(x, n):
    return np.convolve(x, np.ones(n) / n, mode="same")


def soundtrack(path, sr=44100):
    n = int(DUR * sr)
    tt = np.arange(n) / sr
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(42)

    def add(i0, sig, pan=0.5, gain=1.0):
        i0 = max(0, i0)
        i1 = min(n, i0 + len(sig))
        if i1 <= i0:
            return
        s = sig[: i1 - i0] * gain
        L[i0:i1] += s * math.cos(pan * math.pi / 2)
        R[i0:i1] += s * math.sin(pan * math.pi / 2)

    bpm = 90
    beat = 60 / bpm
    seg = beat * 8
    # Am F C G -> no fim, F G C
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
    roots = [33, 29, 36, 31]
    nseg = int(math.ceil(DUR / seg))
    for s in range(nseg):
        ch, root = chords[s % 4], roots[s % 4]
        t0 = s * seg
        ln = seg + 1.6
        lt = np.arange(int(ln * sr)) / sr
        e = np.clip(lt / 1.2, 0, 1) * np.clip((ln - lt) / 1.6, 0, 1)
        e = np.sin(e * np.pi / 2) ** 2
        I = 0.5 + 0.5 * intensity(t0 + seg / 2)
        for m in ch:
            for det, pan in [(-0.0015, 0.25), (0.0015, 0.75)]:
                fq = midi_hz(m) * (1 + det)
                ph = rng.uniform(0, 6.28)
                sig = (np.sin(2 * np.pi * fq * lt + ph) + 0.25 * np.sin(4 * np.pi * fq * lt + ph)) * e
                add(int((t0 - 0.4) * sr), sig, pan, 0.016 * I)
        fq = midi_hz(root + 12)
        add(int((t0 - 0.4) * sr), np.sin(2 * np.pi * fq * lt) * e, 0.5, 0.07 * I)
    # marimba pentatônica
    penta = [57, 60, 62, 64, 67, 69, 72, 74, 76]
    st = 0.0
    k = 0
    while st < DUR - 2:
        I = intensity(st)
        if rng.random() < 0.35 + 0.6 * I:
            ch = chords[int(st // seg) % 4]
            cand = [m for m in penta if (m % 12) in [c % 12 for c in ch]] or penta
            m = cand[(k * 3 + int(rng.integers(0, 3))) % len(cand)] + (12 if I > 0.8 and k % 4 == 0 else 0)
            lt = np.arange(int(1.2 * sr)) / sr
            fq = midi_hz(m)
            sig = (np.sin(2 * np.pi * fq * lt) + 0.3 * np.sin(2 * np.pi * fq * 4 * lt) * np.exp(-lt / 0.05)) \
                * np.exp(-lt / 0.35) * np.clip(lt / 0.003, 0, 1)
            add(int(st * sr), sig, 0.3 + 0.4 * (k % 2), 0.1 * (0.4 + 0.6 * I))
        k += 1
        st += beat / 2
    # percussão leve (tambor grave) quando a intensidade sobe
    st = 0.0
    while st < DUR - 1:
        I = intensity(st)
        ka = 0.3 * clamp((I - 0.55) / 0.45)
        if ka > 0:
            lt = np.arange(int(0.45 * sr)) / sr
            fq = 55 + 70 * np.exp(-lt / 0.03)
            add(int(st * sr), np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.exp(-lt / 0.16), 0.5, ka)
            # chocalho no contratempo
            nz = rng.standard_normal(int(0.08 * sr)) * np.exp(-np.arange(int(0.08 * sr)) / sr / 0.02)
            add(int((st + beat / 2) * sr), nz - _lowpass(nz, 6), 0.6, ka * 0.25)
        st += beat
    # ambiente da mata: vento nas folhas e pássaros (dia), grilos (noite)
    wind = _lowpass(rng.standard_normal(n), 40)
    amb_day = np.interp(tt, [7, 9, 30, 36, 128, 130, 145, 147], [0, 1, 1, 0, 0, 1, 1, 0])
    amb_night = np.interp(tt, [32, 38, 50, 52, 63, 65, 96, 97, 110, 111], [0, 1, 1, 0.8, 0.8, 0, 0, 1, 1, 0])
    L += wind * (amb_day + amb_night * 0.6) * 0.05
    R += np.roll(wind, 900) * (amb_day + amb_night * 0.6) * 0.05
    for _ in range(70):
        tb = float(rng.uniform(8, 30) if rng.random() < 0.7 else rng.uniform(128, 146))
        f0 = rng.uniform(2200, 3800)
        for j in range(int(rng.integers(2, 5))):
            lt = np.arange(int(0.11 * sr)) / sr
            fq = f0 * (1 + 0.35 * np.sin(np.pi * lt / 0.11))
            sig = np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.sin(np.pi * lt / 0.11) ** 2
            add(int((tb + j * 0.14) * sr), sig, float(rng.uniform(0.1, 0.9)), 0.035)
    cr = np.sin(2 * np.pi * 4600 * tt) * (np.sin(2 * np.pi * 28 * tt) > 0.6) * (np.sin(2 * np.pi * 0.7 * tt) > 0)
    L += cr * amb_night * 0.012
    R += np.roll(cr, 3000) * amb_night * 0.012

    # motosserra: dente de serra com ronco
    def chainsaw(t0, t1, gain, far):
        ln = int((t1 - t0) * sr)
        lt = np.arange(ln) / sr
        fq = 95 + 25 * np.sin(2 * np.pi * 0.6 * lt) + 18 * (np.sin(2 * np.pi * 1.7 * lt) > 0.3)
        ph = np.cumsum(fq) / sr
        saw = 2 * (ph % 1.0) - 1 + 0.3 * rng.standard_normal(ln)
        saw = _lowpass(saw, far)
        e = np.clip(lt / 0.5, 0, 1) * np.clip((t1 - t0 - lt) / 0.8, 0, 1)
        add(int(t0 * sr), saw * e, 0.8, gain)

    chainsaw(19.0, 24.4, 0.05, 30)
    chainsaw(98.6, 106.6, 0.08, 14)

    def ping(t0, notes, gain=0.12, step=0.09):
        for j, m in enumerate(notes):
            lt = np.arange(int(1.0 * sr)) / sr
            fq = midi_hz(m)
            sig = (np.sin(2 * np.pi * fq * lt) + 0.2 * np.sin(4 * np.pi * fq * lt)) * np.exp(-lt / 0.3) * np.clip(lt / 0.004, 0, 1)
            add(int((t0 + j * step) * sr), sig, 0.5, gain)

    ping(42.4, [76, 79, 84, 88], 0.12)                 # aldeia online
    ping(53.8, [72, 76, 79], 0.09)                     # notebook liga
    for t0 in (64.8, 68.6, 76.6, 79.4):                # mensagens do chat
        ping(t0, [84, 88], 0.05, 0.06)
    ping(90.0, [72, 79, 84], 0.08)                     # teste do modelo
    ping(100.6, [88, 84, 88, 84], 0.09, 0.12)          # alerta
    ping(106.9, [72, 76, 79, 84], 0.1)                 # floresta protegida
    for t0 in [111.0 + i * 0.7 for i in range(12)]:    # países se acendem
        ping(t0, [91], 0.025)
    # sopros nas trocas de cena
    for tc in CORTES:
        ln = int(1.6 * sr)
        lt = np.arange(ln) / sr
        nz = _lowpass(rng.standard_normal(ln), 25)
        e = (lt / 1.4) ** 2 * np.clip((1.6 - lt) / 0.2, 0, 1)
        add(int((tc - 1.4) * sr), nz * e, 0.5, 0.18)
    # reverb
    ir_len = int(2.4 * sr)
    it = np.arange(ir_len) / sr
    nfft = 1 << int(math.ceil(math.log2(n + ir_len)))
    out = []
    for sig, seed in [(L, 51), (R, 52)]:
        ir = np.random.default_rng(seed).standard_normal(ir_len) * np.exp(-it / 0.6)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(sig, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]
        out.append(sig * 0.8 + wet * 0.35)
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

def _frame(args):
    i, lang = args
    return draw(i / FPS, TXT[lang]).tobytes()


def render(lang, wav, outdir, poster_t, jobs):
    out = os.path.join(outdir, SAIDA[lang] + ".mp4")
    cmd = [ffmpeg_bin(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(DUR * FPS)
    with mp.get_context("fork").Pool(jobs) as pool:
        for i, buf in enumerate(pool.imap(_frame, ((i, lang) for i in range(total)), chunksize=6)):
            p.stdin.write(buf)
            if i % 600 == 0:
                print(f"{lang}: quadro {i}/{total}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg falhou")
    draw(poster_t, TXT[lang]).save(os.path.join(outdir, SAIDA[lang] + ".jpg"), quality=85)
    print("ok:", out, f"{os.path.getsize(out) / 1e6:.1f} MB", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=list(TXT), action="append")
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--stills-dir", default=".")
    ap.add_argument("--outdir", default=os.path.join(REPO, "assets", "video"))
    ap.add_argument("--poster-t", type=float, default=58.0)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()
    langs = args.lang or list(TXT)
    if args.stills:
        os.makedirs(args.stills_dir, exist_ok=True)
        for lang in langs:
            for t in args.stills:
                draw(t, TXT[lang]).save(os.path.join(args.stills_dir, f"{lang}_{t:05.1f}.png"))
        return
    with tempfile.TemporaryDirectory(prefix="kaua_") as tmp:
        wav = os.path.join(tmp, "trilha.wav")
        print("trilha...", flush=True)
        soundtrack(wav)
        for lang in langs:
            render(lang, wav, args.outdir, args.poster_t, args.jobs)


if __name__ == "__main__":
    main()
