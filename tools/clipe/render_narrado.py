#!/usr/bin/env python3
"""Versões narradas dos clipes do Alegrete Summit 2026.

Cada clipe ganha narração em voz neural (pt, en e es; veja voz.py) e uma trilha
eletrônica nova (trilha_summit.py), que abaixa sozinha sob a voz. As versões
originais não mudam: as narradas são arquivos novos, com "-narrado" no nome.

- simbiose, cowmed, chamada e iotedu: a imagem é copiada do vídeo original,
  sem recodificar; só o áudio é novo.
- kaua: a fábula é remontada em até 90 s a partir das cenas originais
  (render_kaua.py), com cortes, trechos acelerados e fusões.

Uso:
    python3 tools/clipe/render_narrado.py                        # tudo
    python3 tools/clipe/render_narrado.py --clipe kaua --lang pt
    python3 tools/clipe/render_narrado.py --clipe cowmed --so-audio /tmp/mix
    python3 tools/clipe/render_narrado.py --clipe kaua --stills 10 40 --stills-dir /tmp/q
"""
import argparse
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", ".."))
VIDEO = os.path.join(REPO, "assets", "video")
sys.path.insert(0, AQUI)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import signal  # noqa: E402

import trilha_summit as ts  # noqa: E402
import voz  # noqa: E402

SR = voz.SR
LANGS = ["pt", "en", "es"]
SUFIXO = {"pt": "", "en": ".en", "es": ".es"}


def T(pt, en, es):
    return {"pt": pt, "en": en, "es": es}


# ------------------------------------------------------------------ roteiros
# Cada fala: (tempo em s, texto). O texto é um dicionário por idioma, ou uma
# chave do TXT do script original (a fala repete a legenda que está na tela).

SIMBIOSE = [
    (1.4, T("Alegrete Summit 2026 apresenta.", "Alegrete Summit 2026 presents.", "Alegrete Summit 2026 presenta.")),
    (8.2, T("A IA sem inovação perde o sentido.", "AI without innovation loses its meaning.",
            "La IA sin innovación pierde el sentido.")),
    (11.3, T("E a inovação sem IA perde a velocidade.", "And innovation without AI loses its speed.",
             "Y la innovación sin IA pierde la velocidad.")),
    (15.1, T("Juntas, formam uma simbiose indissolúvel.", "Together, they form an inseparable symbiosis.",
             "Juntas, forman una simbiosis indisoluble.")),
    (19.6, T("Uma não avança sem a outra.", "Neither moves forward without the other.", "Una no avanza sin la otra.")),
    (24.8, T("No Pampa, a IA chega a serviço de quem produz, cuida, ensina, governa e empreende.",
             "In the Pampa, AI serves those who produce, care, teach, govern and do business.",
             "En el Pampa, la IA llega al servicio de quien produce, cuida, enseña, gobierna y emprende.")),
    (31.4, T("Arroz e água, pecuária, energia, saúde, educação, gestão pública, comércio e logística de fronteira: "
             "cada setor, uma nova conexão.",
             "Rice and water, livestock, energy, health, education, public management, trade and border logistics: "
             "every sector, a new connection.",
             "Arroz y agua, ganadería, energía, salud, educación, gestión pública, comercio y logística de frontera: "
             "cada sector, una nueva conexión.")),
    (42.7, T("A IA aprende com dados.", "AI learns from data.", "La IA aprende de los datos.")),
    (45.3, T("A inovação aprende com pessoas.", "Innovation learns from people.", "La innovación aprende de las personas.")),
    (47.9, T("E há supervisão humana em cada volta.", "And there is human oversight in every turn.",
             "Y hay supervisión humana en cada vuelta.")),
    (52.5, T("Poder público, empresas, academia e sociedade. Inovar é construir pontes.",
             "Public sector, companies, academia and society. Innovating is building bridges.",
             "Poder público, empresas, academia y sociedad. Innovar es construir puentes.")),
    (57.4, T("E a IA é a nova ponte.", "And AI is the new bridge.", "Y la IA es el nuevo puente.")),
    (62.6, T("IA e inovação: uma simbiose indissolúvel e necessária.",
             "AI and innovation: an inseparable and necessary symbiosis.",
             "IA e innovación: una simbiosis indisoluble y necesaria.")),
    (67.2, T("Alegrete Summit 2026. Inovar é construir pontes.", "Alegrete Summit 2026. Innovating is building bridges.",
             "Alegrete Summit 2026. Innovar es construir puentes.")),
]

COWMED = [
    (1.2, T("Casos de sucesso de IA no Brasil. Cowmed: a IA que escuta o rebanho.",
            "Success stories of AI in Brazil. Cowmed: the AI that listens to the herd.",
            "Casos de éxito de IA en Brasil. Cowmed: la IA que escucha al rebaño.")),
    (8.6, T("Tudo começa em Santa Maria, como um projeto de estudantes da UFSM.",
            "It all begins in Santa Maria, as a student project at UFSM.",
            "Todo comienza en Santa María, como un proyecto de estudiantes de la UFSM.")),
    (13.6, T("Foi incubada e se graduou na Pulsar, a incubadora da universidade.",
             "It was incubated at and graduated from Pulsar, the university's incubator.",
             "Fue incubada y se graduó en Pulsar, la incubadora de la universidad.")),
    (18.6, T("O problema: sem dados, o produtor depende de observar o rebanho.",
             "The problem: without data, the farmer depends on watching the herd.",
             "El problema: sin datos, el productor depende de observar el rebaño.")),
    (23.8, T("Cio e doença percebidos tarde significam leite e dinheiro perdidos.",
             "Heat and disease noticed late mean lost milk and lost money.",
             "Celo y enfermedad detectados tarde significan leche y dinero perdidos.")),
    (30.3, T("A solução: uma coleira que faz 25 leituras por segundo.",
             "The solution: a collar that takes 25 readings per second.",
             "La solución: un collar que hace 25 lecturas por segundo.")),
    (34.7, T("A Vic, a IA da empresa, interpreta os dados.", "Vic, the company's own AI, interprets the data.",
             "Vic, la IA propia de la empresa, interpreta los datos.")),
    (38.6, T("E o alerta chega ao celular antes dos sinais clínicos.",
             "And the alert reaches the phone before clinical signs appear.",
             "Y la alerta llega al celular antes de los signos clínicos.")),
    (42.3, T("A IA transforma movimento em diagnóstico precoce.", "AI turns movement into early diagnosis.",
             "La IA convierte el movimiento en diagnóstico precoz.")),
    (46.3, T("Em 2022, captou 5,9 milhões de reais com 547 investidores.",
             "In 2022, it raised 5.9 million reais from 547 investors.",
             "En 2022, captó 5,9 millones de reales de 547 inversores.")),
    (52.0, T("Recorde no Brasil, com 35 mil vacas em mais de 400 fazendas.",
             "A Brazilian record, with 35,000 cows on over 400 farms.",
             "Récord en Brasil, con 35 mil vacas en más de 400 granjas.")),
    (56.5, T("São 100 mil animais monitorados, e receita de cerca de 18 milhões de reais em 2025, "
             "segundo a empresa.",
             "Now 100,000 animals are monitored, with revenue of about 18 million reais in 2025, "
             "per the company.",
             "Hoy son 100 mil animales monitoreados, con ingresos de unos 18 millones de reales en 2025, "
             "según la empresa.")),
    (63.1, T("E a Cowmed já chega ao Paraguai, ao Uruguai e ao México.",
             "Cowmed now reaches Paraguay, Uruguay and Mexico.",
             "Y Cowmed ya llega a Paraguay, Uruguay y México.")),
    (66.3, T("A lição: problema do campo, ciência e incubadora regional.",
             "The lesson: a field problem, science and a regional incubator.",
             "La lección: problema del campo, ciencia e incubadora regional.")),
    (70.5, T("Do Pampa para o mundo. Alegrete Summit 2026.", "From the Pampa to the world. Alegrete Summit 2026.",
             "Del Pampa al mundo. Alegrete Summit 2026.")),
]

CHAMADA = [
    (0.6, T("Alegrete Summit 2026. Dias 29 e 30 de outubro, em Alegrete.",
            "Alegrete Summit 2026. October 29 and 30, in Alegrete.",
            "Alegrete Summit 2026. 29 y 30 de octubre, en Alegrete.")),
    (5.6, T("Tem uma ideia? Um projeto, um negócio, uma pesquisa?",
            "Got an idea? A project, a business, a research question?",
            "¿Tienes una idea? ¿Un proyecto, un negocio, una investigación?")),
    (9.1, T("A conexão que falta pode estar no Summit.", "The connection you're missing may be at the Summit.",
            "La conexión que te falta puede estar en el Summit.")),
    (12.8, T("Inovar é construir pontes: entre quem produz e quem pesquisa, quem empreende e quem investe, "
             "o campo e a cidade.",
             "Innovating is building bridges: between producers and researchers, founders and investors, "
             "the countryside and the city.",
             "Innovar es construir puentes: entre quien produce y quien investiga, quien emprende y quien invierte, "
             "el campo y la ciudad.")),
    (20.7, T("Dezoito conversas no Palco Geek.", "Eighteen talks on the Geek Stage.", "Dieciocho charlas en el Escenario Geek.")),
    (23.45, T("Treze equipes no Bye Bye Boss.", "Thirteen teams at Bye Bye Boss.", "Trece equipos en el Bye Bye Boss.")),
    (26.2, T("Um dia de Ideathon.", "One day of Ideathon.", "Un día de Ideathon.")),
    (28.95, T("E dois dias de Mostra Tecnológica.", "And two days of Technology Showcase.",
              "Y dos días de Muestra Tecnológica.")),
    (31.8, T("Ideias encontram parceiros. Conexões viram negócios.", "Ideas meet partners. Connections become business.",
             "Las ideas encuentran socios. Las conexiones se vuelven negocios.")),
    (35.9, T("Uma conversa pode virar sociedade.", "One conversation can become a partnership.",
             "Una charla puede volverse una sociedad.")),
    (38.7, T("Para quem é?", "Who is it for?", "¿Para quién es?")),
    (40.9, T("Para você.", "For you.", "Para ti.")),
    (42.8, T("29 e 30 de outubro. Gratuito e com certificado.", "October 29 and 30. Free, with a certificate.",
             "29 y 30 de octubre. Gratuito y con certificado.")),
    (46.9, T("Faça sua pré-inscrição!", "Pre-register now!", "¡Haz tu preinscripción!")),
]

IOTEDU = [
    (1.5, "_titulo"),
    (5.4, T("Uma história real, na UNIPAMPA.", "A true story, at UNIPAMPA.", "Una historia real, en la UNIPAMPA.")),
    (7.8, "f1"),
    (12.4, T("Não é hipótese, nem projeção, nem hype. É medição.",
             "It is not a hypothesis, a projection or hype. It is measurement.",
             "No es hipótesis, ni proyección, ni hype. Es medición.")),
    (20.7, "c1"), (27.4, "c2"), (33.2, "c3"), (40.7, "c4"), (47.4, "c5"), (58.7, "c6"), (64.9, "c7"),
    (71.2, T("Cento e vinte e oito vezes mais eficiência. E entregou mais.",
             "One hundred twenty-eight times more efficient. And delivered more.",
             "Ciento veintiocho veces más eficiencia. Y entregó más.")),
    (78.7, "c8"),
    (86.9, T("Essa narrativa está errada.", "That narrative is wrong.", "Esa narrativa está equivocada.")),
    (89.7, "c9"), (94.9, "c10"), (100.5, "c11"),
    (105.1, T("Experiência real, resolução de problemas e domínio da IA fazem a diferença.",
              "Real experience and problem solving, combined with mastery of AI, make the difference.",
              "La experiencia real y la resolución de problemas, sumadas al dominio de la IA, marcan la diferencia.")),
    (110.7, T("A batalha IA contra IA já está acontecendo. É um fato desta semana.",
              "The AI-versus-AI battle is already happening. Not in the future: this week.",
              "La batalla IA contra IA ya está ocurriendo. No es futuro: es un hecho de esta semana.")),
    (116.4, "c14"),
    (122.4, "emp"),
    (128.8, "emp_fim"),
    (134.5, "_q0"), (140.4, "_q1"), (146.3, "_q2"),
    (152.4, "_fim12"), (156.0, "fim3"),
    (161.3, T("Alegrete Summit 2026.", "Alegrete Summit 2026.", "Alegrete Summit 2026.")),
]


def texto_iotedu(chave, L):
    if chave == "_titulo":
        return L["t1"] + " " + L["t2"]
    if chave.startswith("_q"):
        return L["perg"][int(chave[2:])][0]
    if chave == "_fim12":
        return "A IA não nivela. Amplia o gap." if L["fim1"] == "A IA não nivela." else L["fim1"] + " " + L["fim2"]
    return L[chave]


# ------------------------------------------------- a fábula de Kauã em 90 s
# (início, fim, velocidade) em tempo do clipe original; entre trechos não
# contíguos há uma fusão de XF segundos.

XF = 0.5
KAUA_EDL = [
    (0.0, 4.2, 1.0),      # abertura
    (8.8, 14.1, 1.0),     # Kauã chega à aldeia (c1)
    (18.7, 24.3, 1.0),    # fumaça e motosserra (c3)
    (24.3, 30.4, 1.6),    # sem sinal (c4)
    (30.4, 36.1, 1.0),    # a antena (c5)
    (36.1, 42.1, 3.0),    # o trem de satélites
    (42.1, 47.6, 1.0),    # ONLINE (c7)
    (50.2, 55.5, 1.15),   # o notebook (c8)
    (55.5, 62.0, 1.15),   # nunca estudou computação (c9)
    (64.2, 68.6, 1.0),    # o chat com a IA (c10)
    (86.8, 93.6, 1.1),    # código e teste do modelo (c13)
    (96.2, 109.0, 1.35),  # Kaá Sentinela (c14, c15)
    (116.6, 124.6, 1.25),  # sucesso internacional (c17)
    (128.3, 140.0, 1.5),  # a aldeia nova
    (146.2, 150.4, 1.1),  # internet + notebook + IA
    (150.4, 155.8, 0.9),  # a moral (m1)
    (165.8, 172.6, 1.0),  # encerramento
]

KAUA = [
    (1.9, T("Kauã e o poder de criar.", "Kauã and the power to create.", "Kauã y el poder de crear.")),
    (9.3, "c1"), (19.0, "c3"), (24.6, "c4"), (30.7, "c5"), (42.3, "c7"), (50.6, "c8"), (55.8, "c9"),
    (64.6, "c10"), (87.1, "c13"), (96.7, "c14"), (103.3, "c15"), (117.1, "c17"),
    (128.6, T("Com o dinheiro, Kauã investiu na aldeia: energia solar, água potável, posto de saúde e escola conectada.",
              "With the money, Kauã invested in the village: solar power, clean water, a health post and a connected school.",
              "Con el dinero, Kauã invirtió en la aldea: energía solar, agua potable, puesto de salud y escuela conectada.")),
    (146.4, T("Internet, notebook e IA: o poder de criar.", "The internet, a laptop and AI: the power to create.",
              "Internet, una portátil e IA: el poder de crear.")),
    (150.6, "m1"),
    (166.0, "_end"),
]


class Edl:
    def __init__(self, segs, xf=XF):
        self.segs = []
        t = 0.0
        for i, (a, b, v) in enumerate(segs):
            if i and abs(segs[i - 1][1] - a) > 1e-6:
                t -= xf
            self.segs.append((a, b, v, t, t + (b - a) / v))
            t += (b - a) / v
        self.dur = t
        self.xf = xf

    def saida(self, ts):
        """Tempo de saída de um tempo do original."""
        for a, b, v, o0, _ in self.segs:
            if a <= ts < b:
                return o0 + (ts - a) / v
        raise ValueError(f"{ts} s não está na montagem")

    def fontes(self, to):
        """[(tempo no original, peso)] para o quadro no tempo de saída to."""
        ativos = [(a + (to - o0) * v, o0) for a, b, v, o0, o1 in self.segs if o0 <= to < o1]
        if len(ativos) == 1:
            return [(ativos[0][0], 1.0)]
        (t1, _), (t2, o2) = ativos[-2:]
        w = float(np.clip((to - o2) / self.xf, 0, 1))
        return [(t1, 1 - w), (t2, w)]


# ------------------------------------------------------------------ clipes

def clipes():
    import render_iotedu as ri
    import render_kaua as rk
    edl = Edl(KAUA_EDL)
    if edl.dur > 90.0:
        sys.exit(f"a montagem da fábula tem {edl.dur:.1f} s; o limite é 90 s")
    m = edl.saida

    def kaua_txt(chave, L):
        if chave == "_end":
            return "".join(s for s, _ in L["end"])
        return L[chave]

    return {
        "simbiose": dict(
            base="ia-inovacao-simbiose", fonte=lambda lang: "ia-inovacao-simbiose", dur=72.0, falas=SIMBIOSE,
            bpm=110, prog=[(50, ts.MENOR9), (46, ts.MAIOR7), (53, ts.ADD9), (48, ts.SUS)],
            niveis=[(0, 0), (6, 1), (14.5, 3), (24, 2), (40, 3), (52, 2), (62, 4), (67, 2)],
            cortes=[6, 14.5, 24, 40, 52, 62]),
        "cowmed": dict(
            base="cowmed-ia", fonte=lambda lang: "cowmed-ia", dur=75.0, falas=COWMED,
            bpm=104, prog=[(43, ts.ADD9), (50, ts.MAIOR6), (52, ts.MENOR7), (48, ts.MAIOR7)],
            niveis=[(0, 0.5), (8, 1), (18, 2), (30, 3), (46, 4), (56, 3), (66, 2), (70.4, 1)],
            cortes=[8, 18, 30, 46, 56, 66], brilho=0.95),
        "chamada": dict(
            base="alegrete-summit-2026", fonte=lambda lang: "alegrete-summit-2026" + SUFIXO[lang], dur=50.0,
            falas=CHAMADA, bpm=120, prog=[(45, ts.MENOR9), (41, ts.MAIOR7), (48, ts.ADD9), (43, ts.MAIOR6)],
            niveis=[(0, 1), (5.5, 2), (12.5, 3), (20.5, 4), (31.5, 3), (38.5, 2), (42.5, 4), (47.5, 1)],
            cortes=[5.5, 12.5, 20.5, 31.5, 38.5, 42.5], brilho=1.1),
        "iotedu": dict(
            base="revolucao-ia", fonte=lambda lang: "revolucao-ia" + SUFIXO[lang], dur=166.0, falas=IOTEDU,
            texto=lambda chave, lang: texto_iotedu(chave, ri.TXT[lang]),
            bpm=118, prog=[(50, ts.MENOR7), (46, ts.MAIOR7), (53, ts.ADD9), (48, ts.SUS)],
            niveis=[(0, 3), (7.5, 1), (20, 2), (40, 3), (58, 4), (78, 2), (100, 3), (110, 2), (122, 3),
                    (134, 1), (152, 4), (161, 2)],
            cortes=[7.5, 20, 40, 58, 78, 100, 110, 122, 134, 152]),
        "kaua": dict(
            base="kaua-ia", dur=edl.dur, edl=edl, falas=[(m(t), x) for t, x in KAUA],
            texto=lambda chave, lang: kaua_txt(chave, rk.TXT[lang]),
            bpm=96, prog=[(45, ts.MENOR9), (41, ts.MAIOR7), (48, ts.ADD9), (43, ts.MAIOR6)],
            niveis=[(0, 0), (m(8.8), 1), (m(30.4), 2), (m(42.1), 3), (m(50.2), 2), (m(64.2), 3), (m(96.2), 3),
                    (m(116.6), 4), (m(128.3), 3), (m(146.2), 2), (m(165.8), 4), (m(169.5), 1)],
            cortes=[m(8.8), m(30.4), m(42.1), m(50.2), m(64.2), m(96.2), m(116.6), m(128.3), m(146.2),
                    m(165.8)],
            sfx=lambda: kaua_sfx(edl)),
    }


# ------------------------------------------------------------------- áudio

def kaua_sfx(edl):
    """Motosserra ao longe e o alerta do Kaá Sentinela, no tempo da montagem."""
    n = int((edl.dur + 1) * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(5)
    t0, t1 = edl.saida(98.6), edl.saida(106.5)
    ln = int((t1 - t0) * SR)
    tt = np.arange(ln) / SR
    fq = 105 + 18 * np.sin(2 * np.pi * 0.7 * tt) + 25 * (np.sin(2 * np.pi * 0.23 * tt) > 0.3)
    serra = 2 * ((np.cumsum(fq) / SR) % 1) - 1 + 0.3 * rng.standard_normal(ln)
    serra = ts.filtro(serra, "band", [180, 1800]) * np.clip(tt / 0.8, 0, 1) * np.clip((ln / SR - tt) / 0.6, 0, 1)
    i0 = int(t0 * SR)
    out[i0:i0 + ln] += serra * 0.09
    for ta in (100.6, 101.6, 102.6):
        to = edl.saida(ta)
        for j, mm in enumerate((88, 93)):
            ln = int(0.5 * SR)
            tt = np.arange(ln) / SR
            s = np.sin(2 * np.pi * ts.midi_hz(mm) * tt) * np.exp(-tt / 0.12)
            i0 = int((to + j * 0.11) * SR)
            out[i0:i0 + ln] += s * 0.12
    return out


def trilha(c):
    tr = ts.Trilha(c["dur"], c["bpm"], c["prog"], c["niveis"], c["cortes"], brilho=c.get("brilho", 1.0))
    return tr.render()


def faixa_voz(c, lang, avisos):
    """Monta a narração: cada fala no seu tempo, acelerada se não couber."""
    dur = c["dur"]
    falas = c["falas"]
    n = int(dur * SR)
    out = np.zeros(n)

    def texto(x):
        if isinstance(x, dict):
            return x[lang]
        return c["texto"](x, lang)

    jobs = []
    for i, (t0, x) in enumerate(falas):
        fim = falas[i + 1][0] if i + 1 < len(falas) else dur - 0.4
        jobs.append((t0, texto(x), fim - t0 - 0.2))
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda j: voz.cabe(j[1], lang, j[2]), jobs))
    for (t0, txt, jan), (x, rate) in zip(jobs, res):
        d = len(x) / SR
        if d > jan + 0.05:
            avisos.append(f"{lang} {t0:6.1f}s: fala de {d:.1f}s numa janela de {jan:.1f}s: {txt[:50]}")
        i0 = int(t0 * SR)
        i1 = min(n, i0 + len(x))
        out[i0:i1] += x[: i1 - i0]
    return out


def ducking(voz_mono, n, reducao_db=-11.0):
    """Ganho da trilha: abaixa quando há voz (com antecipação e segura entre palavras)."""
    hop = 480
    m = int(np.ceil(len(voz_mono) / hop))
    v = np.pad(voz_mono, (0, m * hop - len(voz_mono))).reshape(m, hop)
    ativo = np.sqrt((v ** 2).mean(axis=1)) > 0.01
    # antecipa 150 ms e segura 450 ms
    ativo = np.convolve(ativo.astype(float), np.ones(61), mode="full")[30: 30 + m] > 0
    alvo = np.where(ativo, 10 ** (reducao_db / 20), 1.0)
    g = np.empty(m)
    acc = 1.0
    for i in range(m):
        k = 0.25 if alvo[i] < acc else 0.05  # ataque ~40 ms, retorno ~200 ms
        acc += (alvo[i] - acc) * k
        g[i] = acc
    ganho = np.interp(np.arange(n), np.arange(m) * hop, g)
    return ganho


def mixa(musica, narr, sfx=None):
    n = musica.shape[1]
    narr = np.pad(narr, (0, max(0, n - len(narr))))[:n]
    narr = ts.filtro(narr, "high", 75)
    # voz em -18 dBFS RMS nos trechos falados
    falado = np.abs(narr) > 0.01
    rms = np.sqrt((narr[falado] ** 2).mean()) if falado.any() else 1.0
    narr = narr * (10 ** (-18 / 20) / rms)
    ir = ts.reverb_ir(0.9, seed=8, brilho=6000)
    sala = signal.fftconvolve(narr, ir[0])[:n] * 0.05
    g = ducking(narr, n)
    mus = musica * 0.36 * g
    mixv = mus + np.vstack([narr + sala, narr + sala])
    if sfx is not None:
        s = np.pad(sfx, (0, max(0, n - len(sfx))))[:n]
        mixv += np.vstack([s, s]) * g
    pico = np.max(np.abs(mixv))
    if pico > 0.98:
        mixv *= 0.98 / pico
    return mixv


def grava_wav(path, x):
    pcm = (np.clip(x.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


AUDIO_OUT = ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "160k"]


# ------------------------------------------------------------------- vídeo

def remuxa(c, lang, wav, saida):
    fonte = os.path.join(VIDEO, c["fonte"](lang) + ".mp4")
    cmd = [voz.ffmpeg_bin(), "-y", "-loglevel", "error", "-i", fonte, "-i", wav,
           "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", *AUDIO_OUT,
           "-t", f"{c['dur']:.3f}", "-movflags", "+faststart", saida]
    subprocess.run(cmd, check=True)
    shutil.copyfile(os.path.join(VIDEO, c["fonte"](lang) + ".jpg"), os.path.splitext(saida)[0] + ".jpg")


_EDL = None
_LANG = None


def quadro_kaua(to, lang, edl):
    import render_kaua as rk
    L = rk.TXT[lang]
    fontes = edl.fontes(to)
    im = rk.draw(fontes[0][0], L)
    if len(fontes) == 2:
        im = Image.blend(im, rk.draw(fontes[1][0], L), fontes[1][1])
    # escurece no fim
    k = float(np.clip((edl.dur - to) / 1.0, 0, 1))
    if k < 1:
        im = Image.blend(Image.new("RGB", im.size), im, k)
    return im


def _quadro(i):
    import render_kaua as rk
    return quadro_kaua(i / rk.FPS, _LANG, _EDL).tobytes()


def render_kaua(c, lang, wav, saida, jobs):
    global _EDL, _LANG
    import render_kaua as rk
    _EDL, _LANG = c["edl"], lang
    cmd = [voz.ffmpeg_bin(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{rk.W}x{rk.H}", "-r", str(rk.FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
           *AUDIO_OUT, "-shortest", "-movflags", "+faststart", saida]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(c["dur"] * rk.FPS)
    with mp.get_context("fork").Pool(jobs) as pool:
        for i, buf in enumerate(pool.imap(_quadro, range(total), chunksize=6)):
            p.stdin.write(buf)
            if i % 600 == 0:
                print(f"  {lang}: quadro {i}/{total}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg falhou")
    quadro_kaua(c["edl"].saida(58.0), lang, c["edl"]).save(os.path.splitext(saida)[0] + ".jpg", quality=85)


# -------------------------------------------------------------------- main

def main():
    todos = clipes()
    ap = argparse.ArgumentParser()
    ap.add_argument("--clipe", choices=list(todos), action="append")
    ap.add_argument("--lang", choices=LANGS, action="append")
    ap.add_argument("--outdir", default=VIDEO)
    ap.add_argument("--so-audio", metavar="DIR", help="grava só a mixagem em WAV nesta pasta")
    ap.add_argument("--checa", action="store_true", help="só confere se as falas cabem nas janelas")
    ap.add_argument("--stills", nargs="*", type=float, help="tempos (s) da montagem da fábula para salvar em PNG")
    ap.add_argument("--stills-dir", default=".")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()
    nomes = args.clipe or list(todos)
    langs = args.lang or LANGS

    if args.stills:
        os.makedirs(args.stills_dir, exist_ok=True)
        for lang in langs:
            for t in args.stills:
                quadro_kaua(t, lang, todos["kaua"]["edl"]).save(os.path.join(args.stills_dir, f"kaua_{lang}_{t:05.1f}.png"))
        return

    avisos = []
    if args.checa:
        for nome in nomes:
            print(f"{nome}: {todos[nome]['dur']:.1f} s", flush=True)
            for lang in langs:
                faixa_voz(todos[nome], lang, avisos)
        for a in avisos:
            print("AVISO:", a)
        return
    for nome in nomes:
        c = todos[nome]
        print(f"{nome}: {c['dur']:.1f} s, trilha...", flush=True)
        musica = trilha(c)
        sfx = c["sfx"]() if "sfx" in c else None
        for lang in langs:
            narr = faixa_voz(c, lang, avisos)
            mixv = mixa(musica, narr, sfx)
            saida = os.path.join(args.outdir, c["base"] + "-narrado" + SUFIXO[lang] + ".mp4")
            if args.so_audio:
                os.makedirs(args.so_audio, exist_ok=True)
                grava_wav(os.path.join(args.so_audio, f"{nome}_{lang}.wav"), mixv)
                continue
            with tempfile.TemporaryDirectory(prefix="narrado_") as tmp:
                wav = os.path.join(tmp, "mix.wav")
                grava_wav(wav, mixv)
                if "edl" in c:
                    render_kaua(c, lang, wav, saida, args.jobs)
                else:
                    remuxa(c, lang, wav, saida)
            print(f"  ok: {saida} ({os.path.getsize(saida) / 1e6:.1f} MB)", flush=True)
    for a in avisos:
        print("AVISO:", a)


if __name__ == "__main__":
    main()
