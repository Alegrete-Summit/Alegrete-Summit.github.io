#!/usr/bin/env python3
"""Clipe "A revolução da IA já começou. E está atropelando", do Alegrete Summit 2026.

Caso real relatado por Diego Kreutz (UNIPAMPA) no projeto de inovação IoTEdu
(https://iotedu.org): uma equipe de 6 alunos levou 7 dias (cerca de 256 horas-pessoa)
numa tarefa que um único aluno de graduação, usando LLMs em alto nível, entregou
melhor e mais completa em 2 horas. Os alunos não são identificados.

Usa o mesmo motor de desenho do clipe da fábula de Kauã (render_kaua.py).

Uso:
    python3 -I tools/clipe/render_iotedu.py                    # pt, en e es
    python3 -I tools/clipe/render_iotedu.py --lang en          # só um idioma
    python3 -I tools/clipe/render_iotedu.py --stills 30 72 --stills-dir /tmp/quadros
"""
import argparse
import math
import multiprocessing as mp
import os
import subprocess
import sys
import tempfile
import wave
from functools import lru_cache

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import numpy as np  # noqa: E402
from PIL import ImageDraw  # noqa: E402

from render_clipe import (  # noqa: E402
    AMBER, FPS, GRAY, GREEN, H, REPO, W, WHITE, clamp, ease, env, eout, ffmpeg_bin, font, lerp, midi_hz, mix, prog,
)
from render_kaua import (  # noqa: E402
    INK, RED, SS, Cv, bump, caption, gradient, laptop_front, logo, person, wrap,
)

DUR = 166.0
T_FATO, T_EQUIPE, T_BACKUP, T_CONTA, T_NARR, T_DIF, T_ENSINO, T_EMPRESAS, T_PERG, T_FIM = (
    7.5, 20.0, 40.0, 58.0, 78.0, 100.0, 110.0, 122.0, 134.0, 152.0)
CORTES = [T_FATO, T_EQUIPE, T_BACKUP, T_CONTA, T_NARR, T_DIF, T_ENSINO, T_EMPRESAS, T_PERG, T_FIM]

SAIDA = {"pt": "revolucao-ia", "en": "revolucao-ia.en", "es": "revolucao-ia.es"}

SKINS = [(232, 190, 160), (196, 140, 100), (150, 98, 62), (110, 72, 48), (214, 168, 128), (176, 120, 84)]
HAIRS = [(40, 30, 24), (24, 20, 18), (120, 80, 40), (24, 20, 18), (60, 40, 28), (160, 120, 70)]
SHIRTS = [(70, 110, 170), (150, 80, 160), (200, 110, 60), (60, 150, 140), (180, 70, 80), (110, 120, 130)]

TXT = {
    "pt": {
        "pre": "ALEGRETE SUMMIT 2026 apresenta",
        "t1": "A revolução da IA já começou.",
        "t2": "E está atropelando.",
        "t3": "Uma história real · projeto de inovação IoTEdu · UNIPAMPA",
        "f1": "Esta semana, num projeto de inovação, aconteceu algo que precisa ser contado.",
        "nao": "Não é",
        "words": ["hipótese", "projeção", "hype"],
        "medicao": "É medição.",
        "h_equipe": "A EQUIPE",
        "roles": ["graduação", "graduação", "mestrado", "mestrado", "mestrado", "mestre"],
        "dia": "dia", "dias": "dias", "hp": "horas-pessoa",
        "c1": "6 alunos considerados bons ou muito bons por todos os professores que os conhecem.",
        "c2": "2 graduandos, 3 mestrandos e 1 mestre.",
        "c3": "Trabalharam durante 7 dias em uma tarefa.",
        "entrega": "entrega",
        "h_backup": "O BACKUP",
        "grad": "graduação",
        "horas": "horas",
        "melhor": "melhor e mais completo",
        "c4": "Um único aluno de graduação, o backup, muito bom e usando LLMs em alto nível…",
        "c5": "…entregou o mesmo resultado, melhor e mais completo, em apenas 2 horas.",
        "h_conta": "A MATEMÁTICA QUE DÓI",
        "b_equipe": "equipe: 256 horas-pessoa",
        "b_backup": "backup: 2 horas",
        "efic": "mais eficiência. E entregou mais.",
        "c6": "Somando as horas de todos, a equipe consumiu cerca de 256 horas-pessoa.",
        "c7": "O backup consumiu 2 horas. E entregou mais, muito mais, do que os outros seis.",
        "h_narr": "A NARRATIVA CONFORTÁVEL",
        "msg": "Dados: um programador sênior aumenta sua produtividade em 80% com LLMs. Um júnior perde 20%. "
               "Por isso, empresas estão proibindo juniores de usar IA.",
        "errada": "ERRADA",
        "bars": [("júnior", "0,8×", "narrativa"), ("sênior", "1,8×", "narrativa"), ("caso real", "128×", "IA em alto nível")],
        "c8": "Circula a ideia de que sêniores ganham 80% com IA e juniores perdem 20%.",
        "c9": "Não é 80% a mais. Não é o dobro. É 128 vezes.",
        "c10": "A IA não nivela. A IA amplia o gap de forma dramática.",
        "h_dif": "O DIFERENCIAL",
        "dif": ["resolver problemas de forma efetiva", "experiência em projetos reais", "domínio no uso de IA"],
        "dif_r": "velocidade sem precedentes",
        "c11": "Os seis também usam LLMs, mas muito longe do nível em que o backup usa.",
        "c12": "Experiência real e resolução de problemas, somadas ao domínio da IA, fazem a diferença.",
        "h_ensino": "IMPLICAÇÕES PARA O ENSINO",
        "ensino": ["o currículo que ensinamos", "as avaliações que aplicamos", "os critérios de um bom aluno",
                   "a formação que entregamos ao mercado", "a relevância da sala de aula"],
        "c13": "A batalha IA contra IA já está acontecendo. Não é futuro: é um fato desta semana.",
        "c14": "E ainda não caiu a ficha para a maioria dos professores de computação.",
        "h_emp": "O RECADO PARA AS EMPRESAS",
        "emp": "Proibir juniores de usar IA é um erro estratégico grave.",
        "emp_pts": ["sufoca quem poderia ter o maior impacto", "os melhores migram para onde podem evoluir",
                    "perde-se a janela crítica de aprendizado"],
        "emp_fim": "Bons juniores devem usar IA. E em alto nível.",
        "h_perg": "O RECADO PARA NÓS, PROFESSORES",
        "perg": [("Você sabe o que seu aluno mais avançado no uso de LLMs é capaz de produzir hoje?",
                  "Se não sabe, está avaliando às cegas."),
                 ("Suas avaliações distinguem quem usa LLMs de forma superficial de quem usa em alto nível?",
                  "Se não distinguem, tratam como iguais realidades completamente diferentes."),
                 ("Você usa LLMs no seu trabalho com a mesma intensidade com que regula o uso pelos alunos?",
                  "Se existe essa assimetria, ela não se sustenta por muito tempo.")],
        "fim1": "A IA não nivela.",
        "fim2": "A IA amplia o gap.",
        "fim3": "A pergunta não é se isso vai chegar até nós. É quanto tempo levamos para perceber que já chegou.",
        "cred": "Relato real de Diego Kreutz (UNIPAMPA) no projeto de inovação IoTEdu · iotedu.org",
        "date": "29 e 30 de outubro · Alegrete/RS",
    },
    "en": {
        "pre": "ALEGRETE SUMMIT 2026 presents",
        "t1": "The AI revolution has already begun.",
        "t2": "And it is running us over.",
        "t3": "A true story · IoTEdu innovation project · UNIPAMPA",
        "f1": "This week, in an innovation project, something happened that needs to be told.",
        "nao": "It is not",
        "words": ["a hypothesis", "a projection", "hype"],
        "medicao": "It is measurement.",
        "h_equipe": "THE TEAM",
        "roles": ["undergrad", "undergrad", "master's", "master's", "master's", "MSc"],
        "dia": "day", "dias": "days", "hp": "person-hours",
        "c1": "6 students rated good or very good by every professor who knows them.",
        "c2": "2 undergrads, 3 master's students and 1 MSc graduate.",
        "c3": "They worked on a task for 7 days.",
        "entrega": "delivery",
        "h_backup": "THE BACKUP",
        "grad": "undergrad",
        "horas": "hours",
        "melhor": "better and more complete",
        "c4": "A single undergraduate, the backup, very good and using LLMs at a high level…",
        "c5": "…delivered the same result, better and more complete, in just 2 hours.",
        "h_conta": "THE MATH THAT HURTS",
        "b_equipe": "team: 256 person-hours",
        "b_backup": "backup: 2 hours",
        "efic": "more efficient. And delivered more.",
        "c6": "Adding up everyone's hours, the team used about 256 person-hours.",
        "c7": "The backup used 2 hours. And delivered more, much more, than the other six.",
        "h_narr": "THE COMFORTABLE NARRATIVE",
        "msg": "Data: a senior programmer boosts productivity by 80% with LLMs. A junior loses 20%. "
               "That is why companies are banning juniors from using AI.",
        "errada": "WRONG",
        "bars": [("junior", "0.8×", "narrative"), ("senior", "1.8×", "narrative"), ("real case", "128×", "high-level AI")],
        "c8": "The story going around: seniors gain 80% with AI and juniors lose 20%.",
        "c9": "It is not 80% more. It is not double. It is 128 times.",
        "c10": "AI does not level the field. AI widens the gap dramatically.",
        "h_dif": "THE DIFFERENTIATOR",
        "dif": ["solving problems effectively", "experience in real projects", "mastery of AI"],
        "dif_r": "unprecedented speed",
        "c11": "The six also use LLMs, but nowhere near the level the backup does.",
        "c12": "Real experience and problem solving, combined with mastery of AI, make the difference.",
        "h_ensino": "IMPLICATIONS FOR TEACHING",
        "ensino": ["the curriculum we teach", "the assessments we give", "the criteria for a good student",
                   "the training we deliver to the market", "the relevance of the classroom"],
        "c13": "The AI-versus-AI battle is already happening. Not in the future: this week.",
        "c14": "And most computing professors have not realized it yet.",
        "h_emp": "A MESSAGE TO COMPANIES",
        "emp": "Banning juniors from using AI is a serious strategic mistake.",
        "emp_pts": ["it stifles those who could have the greatest impact", "the best ones move to where they can grow",
                    "the critical learning window is lost"],
        "emp_fim": "Good juniors should use AI. At a high level.",
        "h_perg": "A MESSAGE TO US, PROFESSORS",
        "perg": [("Do you know what your most advanced LLM-using student can produce today?",
                  "If not, you are grading blind."),
                 ("Do your assessments tell superficial LLM use apart from high-level use?",
                  "If not, they treat completely different realities as equal."),
                 ("Do you use LLMs in your own work as intensely as you regulate your students' use?",
                  "If that asymmetry exists, it will not hold for long.")],
        "fim1": "AI does not level the field.",
        "fim2": "AI widens the gap.",
        "fim3": "The question is not whether this will reach us. It is how long it takes us to see it already has.",
        "cred": "A true account by Diego Kreutz (UNIPAMPA) from the IoTEdu innovation project · iotedu.org",
        "date": "October 29–30 · Alegrete, RS, Brazil",
    },
    "es": {
        "pre": "ALEGRETE SUMMIT 2026 presenta",
        "t1": "La revolución de la IA ya comenzó.",
        "t2": "Y está arrollando.",
        "t3": "Una historia real · proyecto de innovación IoTEdu · UNIPAMPA",
        "f1": "Esta semana, en un proyecto de innovación, ocurrió algo que hay que contar.",
        "nao": "No es",
        "words": ["hipótesis", "proyección", "hype"],
        "medicao": "Es medición.",
        "h_equipe": "EL EQUIPO",
        "roles": ["grado", "grado", "maestría", "maestría", "maestría", "magíster"],
        "dia": "día", "dias": "días", "hp": "horas-persona",
        "c1": "6 alumnos considerados buenos o muy buenos por todos los profesores que los conocen.",
        "c2": "2 de grado, 3 de maestría y 1 magíster.",
        "c3": "Trabajaron durante 7 días en una tarea.",
        "entrega": "entrega",
        "h_backup": "EL BACKUP",
        "grad": "grado",
        "horas": "horas",
        "melhor": "mejor y más completo",
        "c4": "Un único alumno de grado, el backup, muy bueno y usando LLMs a alto nivel…",
        "c5": "…entregó el mismo resultado, mejor y más completo, en apenas 2 horas.",
        "h_conta": "LA MATEMÁTICA QUE DUELE",
        "b_equipe": "equipo: 256 horas-persona",
        "b_backup": "backup: 2 horas",
        "efic": "más eficiencia. Y entregó más.",
        "c6": "Sumando las horas de todos, el equipo consumió cerca de 256 horas-persona.",
        "c7": "El backup consumió 2 horas. Y entregó más, mucho más, que los otros seis.",
        "h_narr": "LA NARRATIVA CÓMODA",
        "msg": "Datos: un programador sénior aumenta su productividad un 80% con LLMs. Un júnior pierde un 20%. "
               "Por eso las empresas están prohibiendo que los júniors usen IA.",
        "errada": "ERRÓNEA",
        "bars": [("júnior", "0,8×", "narrativa"), ("sénior", "1,8×", "narrativa"), ("caso real", "128×", "IA a alto nivel")],
        "c8": "Circula la idea de que los séniors ganan un 80% con IA y los júniors pierden un 20%.",
        "c9": "No es un 80% más. No es el doble. Es 128 veces.",
        "c10": "La IA no nivela. La IA amplía la brecha de forma dramática.",
        "h_dif": "EL DIFERENCIAL",
        "dif": ["resolver problemas con eficacia", "experiencia en proyectos reales", "dominio de la IA"],
        "dif_r": "velocidad sin precedentes",
        "c11": "Los seis también usan LLMs, pero muy lejos del nivel del backup.",
        "c12": "La experiencia real y la resolución de problemas, sumadas al dominio de la IA, marcan la diferencia.",
        "h_ensino": "IMPLICACIONES PARA LA ENSEÑANZA",
        "ensino": ["el currículo que enseñamos", "las evaluaciones que aplicamos", "los criterios de un buen alumno",
                   "la formación que entregamos al mercado", "la relevancia del aula"],
        "c13": "La batalla IA contra IA ya está ocurriendo. No es futuro: es un hecho de esta semana.",
        "c14": "Y la mayoría de los profesores de computación todavía no se dio cuenta.",
        "h_emp": "EL MENSAJE PARA LAS EMPRESAS",
        "emp": "Prohibir que los júniors usen IA es un grave error estratégico.",
        "emp_pts": ["asfixia a quienes podrían tener mayor impacto", "los mejores migran a donde pueden crecer",
                    "se pierde la ventana crítica de aprendizaje"],
        "emp_fim": "Los buenos júniors deben usar IA. Y a alto nivel.",
        "h_perg": "EL MENSAJE PARA NOSOTROS, PROFESORES",
        "perg": [("¿Sabes lo que tu alumno más avanzado en el uso de LLMs es capaz de producir hoy?",
                  "Si no lo sabes, estás evaluando a ciegas."),
                 ("¿Tus evaluaciones distinguen el uso superficial de LLMs del uso a alto nivel?",
                  "Si no, tratan como iguales realidades completamente distintas."),
                 ("¿Usas LLMs en tu trabajo con la misma intensidad con que regulas su uso por los alumnos?",
                  "Si existe esa asimetría, no se sostiene por mucho tiempo.")],
        "fim1": "La IA no nivela.",
        "fim2": "La IA amplía la brecha.",
        "fim3": "La pregunta no es si esto llegará a nosotros. Es cuánto tardamos en darnos cuenta de que ya llegó.",
        "cred": "Relato real de Diego Kreutz (UNIPAMPA) en el proyecto de innovación IoTEdu · iotedu.org",
        "date": "29 y 30 de octubre · Alegrete/RS",
    },
}


# ---------------------------------------------------------------- utilidades

@lru_cache(None)
def fundo():
    im = gradient((5, 9, 13), (10, 20, 22))
    d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 40):
        d.line([(x * SS, 0), (x * SS, H * SS)], fill=(25, 245, 140, 9), width=SS)
    for y in range(0, H, 40):
        d.line([(0, y * SS), (W * SS, y * SS)], fill=(25, 245, 140, 9), width=SS)
    return im


def header(cv, t, a0, a1, s, c=GREEN):
    a = env(t, a0, a1, 0.5, 0.5)
    cv.text((W / 2, 56), s, "bold", 22, c, a)
    wd = font("bold", 22).getlength(s)
    cv.line([(W / 2 - wd / 2, 74), (W / 2 + wd / 2, 74)], c, 2, a * 0.6)


def block(cv, s, y, f, size, c, a, maxw=1080, lh=1.25):
    """Parágrafo centralizado com quebra de linha; y é o centro vertical."""
    lines = wrap(s, f, size, maxw)
    step = size * lh
    y0 = y - (len(lines) - 1) * step / 2
    for i, l in enumerate(lines):
        cv.text((W / 2, y0 + i * step), l, f, size, c, a)
    return len(lines) * step


def bar(cv, x0, y, wd, k, c, a, hgt=26, back=(30, 36, 42)):
    cv.rect((x0, y - hgt / 2, x0 + wd, y + hgt / 2), back, a, r=hgt / 2)
    if k > 0:
        cv.rect((x0, y - hgt / 2, x0 + max(hgt, wd * k), y + hgt / 2), c, a, r=hgt / 2)


def clock(cv, cx, cy, r, turns, c, a):
    cv.circ((cx, cy), r, (20, 26, 30), a)
    cv.circ((cx, cy), r, c, a, w=3)
    for i in range(12):
        th = i * math.pi / 6
        cv.line([(cx + math.cos(th) * r * 0.82, cy + math.sin(th) * r * 0.82),
                 (cx + math.cos(th) * r * 0.92, cy + math.sin(th) * r * 0.92)], c, 2, a * 0.7)
    th = turns * 2 * math.pi - math.pi / 2
    cv.line([(cx, cy), (cx + math.cos(th) * r * 0.75, cy + math.sin(th) * r * 0.75)], WHITE, 4, a)
    th2 = turns * 2 * math.pi / 12 - math.pi / 2
    cv.line([(cx, cy), (cx + math.cos(th2) * r * 0.5, cy + math.sin(th2) * r * 0.5)], WHITE, 6, a)
    cv.circ((cx, cy), 6, c, a)


def streaks(cv, t, t0, a=1.0):
    """Rajadas de luz atravessando a tela: a revolução passando."""
    for i in range(14):
        u = (t - t0) * 1.6 - i * 0.07
        if not 0 < u < 1.4:
            continue
        y = 90 + (i * 47) % 560
        x1 = -200 + u * (W + 600)
        ln = 260 + (i % 4) * 90
        c = GREEN if i % 3 else AMBER
        cv.line([(x1 - ln, y), (x1, y)], c, 2 + (i % 3), a * 0.8 * (1 - clamp(u - 1)))


# ------------------------------------------------------------------- cenas

def scene_intro(cv, t, L):
    a = env(t, 0, T_FATO, 0.4, 0.6)
    streaks(cv, t, 2.6, a)
    logo(cv, W / 2, 112, 54, prog(t, 0.3, 1.8), a)
    cv.text((W / 2, 176), L["pre"], "bold", 20, GRAY, a * ease(prog(t, 0.9, 1.7)))
    k = ease(prog(t, 1.6, 2.4))
    cv.text((W / 2, 290 + (1 - k) * 12), L["t1"], "russo", 54, WHITE, a * k)
    k2 = eout(prog(t, 3.0, 3.5))
    shake = math.sin(t * 70) * 6 * (1 - prog(t, 3.3, 4.0)) if t > 3.0 else 0
    cv.text((W / 2 - (1 - k2) * 700 + shake, 372), L["t2"], "russo", 54, AMBER, a * k2)
    k3 = ease(prog(t, 4.3, 5.1))
    cv.text((W / 2, 470), L["t3"], "semi", 24, GREEN, a * k3)


def scene_fato(cv, t, L):
    a = env(t, T_FATO, T_EQUIPE, 0.5, 0.5)
    block(cv, L["f1"], 150, "semi", 34, WHITE, a * ease(prog(t, 7.8, 8.6)), maxw=1000)
    k = ease(prog(t, 9.6, 10.2))
    cv.text((W / 2, 280), L["nao"], "med", 26, GRAY, a * k)
    xs = [W / 2 - 300, W / 2, W / 2 + 300]
    for i, w in enumerate(L["words"]):
        t0 = 10.2 + i * 1.1
        kw = ease(prog(t, t0, t0 + 0.4))
        cv.text((xs[i], 340), w, "semi", 40, WHITE, a * kw * (1 - 0.45 * ease(prog(t, t0 + 0.6, t0 + 0.9))))
        ks = ease(prog(t, t0 + 0.5, t0 + 0.8))
        if ks > 0:
            wd = font("semi", 40).getlength(w) / 2 + 12
            cv.line([(xs[i] - wd, 342), (xs[i] - wd + 2 * wd * ks, 336)], RED, 5, a)
    km = ease(prog(t, 14.0, 14.8))
    cv.text((W / 2, 470), L["medicao"], "russo", 70, GREEN, a * km)
    # régua
    kr = ease(prog(t, 14.6, 16.0))
    x0, x1, y = W / 2 - 300, W / 2 + 300, 540
    cv.line([(x0, y), (x0 + (x1 - x0) * kr, y)], GREEN, 3, a)
    for i in range(31):
        xx = x0 + i * 20
        if xx > x0 + (x1 - x0) * kr:
            break
        cv.line([(xx, y), (xx, y - (18 if i % 5 == 0 else 9))], GREEN, 2, a)


POS6 = [W / 2 + (i - 2.5) * 180 for i in range(6)]


def scene_equipe(cv, t, L):
    a = env(t, T_EQUIPE, T_BACKUP, 0.5, 0.5)
    header(cv, t, T_EQUIPE, T_BACKUP, L["h_equipe"])
    fy = 470
    for i, x in enumerate(POS6):
        k = ease(prog(t, 20.4 + i * 0.25, 21.0 + i * 0.25)) * a
        typing = math.sin(t * 9 + i) * 3
        person(cv, x, fy, 0.6, t + i, arms=((24, 70 + typing), (24, 70 - typing)), shirt=SHIRTS[i], hair=HAIRS[i],
               skin=SKINS[i], paint=False, necklace=False, a=k, seed=i, mouth="o" if t > 34 else "smile")
        if k > 0.02:
            laptop_front(cv, x, fy - 72, 70, 1.0, back=True)
        cv.text((x, fy + 22), L["roles"][i], "semi", 18, GRAY, k)
    # dias e horas-pessoa
    u = ease(prog(t, 25.0, 38.0))
    dia = 1 + int(6 * u + 0.0001)
    kc = ease(prog(t, 24.6, 25.4)) * a
    cv.text((W / 2 - 170, 150), f"{dia} {L['dia'] if dia == 1 else L['dias']}", "russo", 48, WHITE, kc)
    cv.text((W / 2 + 170, 150), f"{int(256 * u)} {L['hp']}", "russo", 40, AMBER, kc)
    # os 7 dias do calendário
    for d in range(7):
        x = W / 2 + (d - 3) * 44
        cv.rect((x - 16, 214, x + 16, 246), None, kc, r=5, outline=(90, 100, 108), w=2)
        kd = clamp(7 * u - d)
        if kd > 0:
            cv.rect((x - 12, 218, x + 12, 242), AMBER, kc * kd, r=3)
    # barra de progresso
    kb = ease(prog(t, 25.0, 38.0))
    cv.text((150, 560), L["entrega"], "semi", 18, GRAY, kc, anchor="rm")
    bar(cv, 170, 560, 800, kb, mix(GREEN, (60, 120, 100), 0.4), kc)
    caption(cv, t, 20.6, 27.0, L["c1"])
    caption(cv, t, 27.3, 32.8, L["c2"])
    caption(cv, t, 33.1, 39.6, L["c3"])


def scene_backup(cv, t, L):
    a = env(t, T_BACKUP, T_CONTA, 0.5, 0.5)
    header(cv, t, T_BACKUP, T_CONTA, L["h_backup"], AMBER)
    x, fy = 380, 470
    k = ease(prog(t, 40.3, 41.0)) * a
    typing = math.sin(t * 16) * 4
    on = ease(prog(t, 42.0, 43.0))
    cv.glow((x, fy - 160), 200, GREEN, on * 0.5 * a)
    person(cv, x, fy, 0.9, t, arms=((24, 70 + typing), (24, 70 - typing)), shirt=(30, 60, 50), hair=(30, 24, 20),
           skin=(200, 150, 110), paint=False, necklace=False, a=k, seed=9)
    if k > 0.02:
        laptop_front(cv, x, fy - 108, 104, 1.0, back=True)
    # fluxo de código e de mensagens saindo do notebook
    if t > 42.5:
        for i in range(16):
            u = ((t - 42.5) * 0.7 + i / 16) % 1.0
            px = x + 60 + u * 360
            py = fy - 200 + math.sin(i * 1.9) * 110 - u * 40
            wd = 30 + (i * 37) % 60
            cv.rect((px, py - 4, px + wd, py + 4), GREEN if i % 3 else AMBER, a * on * (1 - u) * 0.8, r=4)
    # relógio de 2 horas
    kc = ease(prog(t, 43.0, 43.8)) * a
    turns = 2 * ease(prog(t, 44.0, 49.0))
    clock(cv, 940, 250, 110, turns, AMBER, kc)
    cv.text((940, 400), f"{turns:.1f}".replace(".", "," if L is not TXT["en"] else ".") + " " + L["horas"], "russo", 40,
            WHITE, kc)
    cv.text((x, fy + 24), L["grad"], "semi", 18, GRAY, k)
    kb = ease(prog(t, 44.0, 49.0))
    cv.text((150, 560), L["entrega"], "semi", 18, GRAY, kc, anchor="rm")
    bar(cv, 170, 560, 800, kb, GREEN, kc)
    ke = ease(prog(t, 49.4, 50.6))
    if ke > 0:
        cv.rect((170 + 800 - 20, 547, 170 + 800 + 180 * ke, 573), AMBER, kc, r=13)
        cv.text((1060, 524), L["melhor"], "bold", 20, AMBER, kc * ke)
    caption(cv, t, 40.6, 47.0, L["c4"])
    caption(cv, t, 47.3, 57.6, L["c5"])


def scene_conta(cv, t, L):
    a = env(t, T_CONTA, T_NARR, 0.5, 0.5)
    header(cv, t, T_CONTA, T_NARR, L["h_conta"], RED)
    x0, wd = 170, 940
    k1 = ease(prog(t, 58.6, 61.6))
    cv.text((x0, 150), L["b_equipe"], "semi", 26, WHITE, a * ease(prog(t, 58.4, 59.0)), anchor="lm")
    bar(cv, x0, 192, wd, k1, (120, 128, 136), a, hgt=34)
    k2 = ease(prog(t, 64.8, 65.6))
    cv.text((x0, 252), L["b_backup"], "semi", 26, WHITE, a * k2, anchor="lm")
    cv.rect((x0, 277, x0 + wd * 2 / 256 + 4, 311), GREEN, a * k2, r=3)
    ke = ease(prog(t, 69.6, 70.4))
    cv.runs(W / 2, 400, [("256", WHITE), (" ÷ ", GRAY), ("2", GREEN), (" =", GRAY)], "russo", 56, a * ke)
    kb = eout(prog(t, 71.0, 71.6))
    if kb > 0:
        sz = int(130 + 40 * (1 - kb))
        cv.glow((W / 2, 510), 240, AMBER, a * kb * 0.7)
        cv.text((W / 2, 510), "128×", "russo", sz, AMBER, a * kb)
    cv.text((W / 2, 610), L["efic"], "semi", 28, WHITE, a * ease(prog(t, 72.4, 73.2)))
    caption(cv, t, 58.6, 64.4, L["c6"], y=676)
    caption(cv, t, 64.8, 69.4, L["c7"], y=676)


def scene_narr(cv, t, L):
    a = env(t, T_NARR, T_DIF, 0.5, 0.5)
    header(cv, t, T_NARR, T_DIF, L["h_narr"], GRAY)
    # mensagem recebida
    km = ease(prog(t, 78.4, 79.2)) * (1 - ease(prog(t, 86.0, 86.8)))
    if km > 0:
        lines = wrap(L["msg"], "med", 26, 780)
        hgt = len(lines) * 36 + 40
        y0 = 300 - hgt / 2
        cv.text_box((W / 2 - 420, y0, W / 2 + 420, y0 + hgt), (30, 40, 36), a * km, r=20, outline=(70, 90, 80), w=1)
        for i, l in enumerate(lines):
            cv.text((W / 2 - 390, y0 + 38 + i * 36), l, "med", 26, WHITE, a * km, anchor="lm")
        ks = ease(prog(t, 82.6, 83.0))
        if ks > 0:
            sz = int(56 + 30 * (1 - ks))
            hw = font("russo", 56).getlength(L["errada"]) / 2 + 24
            cx = W / 2 + 420 - hw
            cv.text_box((cx - hw, 356, cx + hw, 428), None, a * km * ks, r=10, outline=RED, w=5)
            cv.text((cx, 392), L["errada"], "russo", sz, RED, a * km * ks)
    # gráfico: o gap
    kg = ease(prog(t, 86.8, 87.6)) * a
    if kg > 0:
        base = 560
        xs = [380, 640, 900]
        vals = [0.8, 1.8, 128.0]
        for i, ((lab, v, sub), val) in enumerate(zip(L["bars"], vals)):
            kk = ease(prog(t, 87.4 + i * 1.0, 88.6 + i * 1.6))
            hmax = 400
            hh = max(4, hmax * val / 128.0 * kk)
            c = [GRAY, GRAY, AMBER][i]
            cv.rect((xs[i] - 60, base - hh, xs[i] + 60, base), c, kg, r=6)
            cv.text((xs[i], base - hh - 28), v, "russo", 40 if i == 2 else 30, c, kg * ease(prog(t, 87.6 + i, 88.2 + i)))
            cv.text((xs[i], base + 24), lab, "semi", 22, WHITE, kg)
            cv.text((xs[i], base + 50), sub, "med", 17, GRAY, kg)
    caption(cv, t, 78.6, 85.8, L["c8"], y=676)
    caption(cv, t, 89.6, 94.4, L["c9"], y=676)
    caption(cv, t, 94.8, 99.6, L["c10"], y=676, c=AMBER)


def chip(cv, cx, cy, s, c, a, size=24):
    wd = font("semi", size).getlength(s) + 44
    cv.text_box((cx - wd / 2, cy - size * 1.0, cx + wd / 2, cy + size * 1.0), mix(INK, c, 0.15), a, r=size, outline=c, w=2)
    cv.text((cx, cy), s, "semi", size, WHITE, a)
    return wd


def scene_dif(cv, t, L):
    a = env(t, T_DIF, T_ENSINO, 0.5, 0.5)
    header(cv, t, T_DIF, T_ENSINO, L["h_dif"], AMBER)
    ys = [190, 290, 390]
    for i, s in enumerate(L["dif"]):
        k = ease(prog(t, 100.4 + i * 0.8, 101.0 + i * 0.8)) * a
        chip(cv, W / 2, ys[i], s, [AMBER, AMBER, GREEN][i], k)
        if i < 2:
            cv.text((W / 2, (ys[i] + ys[i + 1]) / 2), "+", "bold", 30, GRAY, k)
    kr = ease(prog(t, 103.4, 104.2)) * a
    cv.text((W / 2, 460), "=", "bold", 36, GRAY, kr)
    cv.glow((W / 2, 530), 200, GREEN, kr * 0.5)
    cv.text((W / 2, 530), L["dif_r"], "russo", 46, GREEN, kr)
    caption(cv, t, 100.4, 104.8, L["c11"], y=650)
    caption(cv, t, 105.1, 109.6, L["c12"], y=650)


def scene_ensino(cv, t, L):
    a = env(t, T_ENSINO, T_EMPRESAS, 0.5, 0.5)
    header(cv, t, T_ENSINO, T_EMPRESAS, L["h_ensino"])
    x0 = 340
    for i, s in enumerate(L["ensino"]):
        k = ease(prog(t, 110.6 + i * 0.7, 111.2 + i * 0.7)) * a
        y = 150 + i * 78
        cv.rect((x0 - 14, y - 14, x0 + 14, y + 14), None, k, r=4, outline=AMBER, w=3)
        kc = ease(prog(t, 111.0 + i * 0.7, 111.4 + i * 0.7))
        if kc > 0:
            cv.line([(x0 - 8, y), (x0 - 2, y + 8), (x0 + 10, y - 9)], AMBER, 4, k * kc)
        cv.text((x0 + 36, y), s, "semi", 32, WHITE, k, anchor="lm")
    caption(cv, t, 110.6, 116.0, L["c13"], y=640)
    caption(cv, t, 116.3, 121.6, L["c14"], y=640, c=AMBER)


def scene_empresas(cv, t, L):
    a = env(t, T_EMPRESAS, T_PERG, 0.5, 0.5)
    header(cv, t, T_EMPRESAS, T_PERG, L["h_emp"], AMBER)
    block(cv, L["emp"], 170, "russo", 44, WHITE, a * ease(prog(t, 122.4, 123.2)), maxw=1000)
    for i, s in enumerate(L["emp_pts"]):
        k = ease(prog(t, 124.2 + i * 1.2, 124.8 + i * 1.2)) * a
        y = 320 + i * 72
        cv.circ((300, y), 8, RED, k)
        cv.text((330, y), s, "semi", 30, WHITE, k, anchor="lm")
    kf = ease(prog(t, 128.6, 129.4)) * a
    cv.glow((W / 2, 580), 220, GREEN, kf * 0.4)
    cv.text((W / 2, 580), L["emp_fim"], "russo", 40, GREEN, kf)


def scene_perg(cv, t, L):
    a = env(t, T_PERG, T_FIM, 0.5, 0.5)
    header(cv, t, T_PERG, T_FIM, L["h_perg"])
    for i, (q, r) in enumerate(L["perg"]):
        t0 = T_PERG + 0.3 + i * 5.9
        k = env(t, t0, t0 + 5.9, 0.5, 0.5) * a
        if k <= 0:
            continue
        cv.text((W / 2, 170), f"{i + 1}/3", "russo", 64, AMBER, k)
        block(cv, q, 330, "semi", 42, WHITE, k, maxw=1000)
        kr = ease(prog(t, t0 + 2.4, t0 + 3.0))
        block(cv, r, 500, "semi", 30, GREEN, k * kr, maxw=1000)


def scene_fim(cv, t, L):
    a = env(t, T_FIM, DUR + 1, 0.5, 0.1) * (1 - ease(prog(t, DUR - 1.6, DUR - 0.2)))
    # duas curvas que se afastam: o gap
    kg = ease(prog(t, T_FIM, T_FIM + 4))
    pts1, pts2 = [], []
    for i in range(61):
        u = i / 60
        if u > kg:
            break
        x = 80 + u * 1120
        pts1.append((x, 660 - 30 * u))
        pts2.append((x, 660 - 300 * u ** 3.2))
    cv.line(pts1, GRAY, 3, a * 0.35)
    cv.line(pts2, AMBER, 4, a * 0.35)
    k1 = ease(prog(t, 152.4, 153.2))
    cv.text((W / 2, 130), L["fim1"], "russo", 58, WHITE, a * k1)
    k2 = ease(prog(t, 153.6, 154.4))
    cv.text((W / 2, 210), L["fim2"], "russo", 58, AMBER, a * k2)
    k3 = ease(prog(t, 155.4, 156.2)) * (1 - ease(prog(t, 160.4, 161.0)))
    block(cv, L["fim3"], 360, "semi", 34, WHITE, a * k3, maxw=980)
    k4 = ease(prog(t, 161.0, 161.8))
    logo(cv, W / 2, 350, 70, prog(t, 160.8, 162.2), a)
    cv.text((W / 2, 432), "ALEGRETE SUMMIT 2026", "bold", 28, WHITE, a * k4)
    cv.text((W / 2, 472), L["date"], "semi", 22, GRAY, a * k4)
    cv.text((W / 2, 560), L["cred"], "med", 20, GREEN, a * ease(prog(t, 156.0, 156.8)))


SCENES = [(0.0, T_FATO, scene_intro), (T_FATO, T_EQUIPE, scene_fato), (T_EQUIPE, T_BACKUP, scene_equipe),
          (T_BACKUP, T_CONTA, scene_backup), (T_CONTA, T_NARR, scene_conta), (T_NARR, T_DIF, scene_narr),
          (T_DIF, T_ENSINO, scene_dif), (T_ENSINO, T_EMPRESAS, scene_ensino), (T_EMPRESAS, T_PERG, scene_empresas),
          (T_PERG, T_FIM, scene_perg), (T_FIM, DUR + 1, scene_fim)]


def draw(t, L):
    cv = Cv(fundo())
    for a, b, fn in SCENES:
        if a <= t < b:
            fn(cv, t, L)
            break
    black = max(1 - clamp(t / 0.6), ease(prog(t, DUR - 1.0, DUR - 0.1)))
    return cv.render(black)


# ------------------------------------------------------------------ trilha

def intensity(t):
    keys = [(0, 0.3), (2.6, 0.9), (7.5, 0.35), (20, 0.4), (40, 0.6), (44, 0.95), (58, 0.6), (70, 0.8), (71, 1.0),
            (78, 0.45), (88, 0.7), (100, 0.6), (110, 0.55), (122, 0.75), (134, 0.5), (152, 0.8), (166, 0.0)]
    xs, ys = zip(*keys)
    return float(np.interp(t, xs, ys))


def _lowpass(x, n):
    return np.convolve(x, np.ones(n) / n, mode="same")


def soundtrack(path, sr=44100):
    """Trilha tensa e pulsante: Dm–B♭–F–C a 112 bpm, baixo em colcheias, tique-taque e impactos."""
    n = int(DUR * sr)
    tt = np.arange(n) / sr
    L = np.zeros(n)
    R = np.zeros(n)
    rng = np.random.default_rng(128)

    def add(i0, sig, pan=0.5, gain=1.0):
        i0 = max(0, i0)
        i1 = min(n, i0 + len(sig))
        if i1 > i0:
            s = sig[: i1 - i0] * gain
            L[i0:i1] += s * math.cos(pan * math.pi / 2)
            R[i0:i1] += s * math.sin(pan * math.pi / 2)

    beat = 60 / 112
    seg = beat * 8
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [53, 57, 60, 65], [48, 55, 60, 64]]
    roots = [38, 34, 41, 36]
    for s in range(int(math.ceil(DUR / seg))):
        t0 = s * seg
        ch, root = chords[s % 4], roots[s % 4]
        ln = seg + 1.2
        lt = np.arange(int(ln * sr)) / sr
        e = np.sin(np.clip(lt / 0.8, 0, 1) * np.clip((ln - lt) / 1.2, 0, 1) * np.pi / 2) ** 2
        I = intensity(t0 + seg / 2)
        for m in ch:
            for det, pan in [(-0.002, 0.2), (0.002, 0.8)]:
                fq = midi_hz(m) * (1 + det)
                saw = sum(np.sin(2 * np.pi * fq * h * lt) / h for h in range(1, 6))
                add(int((t0 - 0.3) * sr), saw * e, pan, 0.008 * (0.5 + 0.5 * I))
        # baixo em colcheias
        for j in range(16):
            st = t0 + j * beat / 2
            ll = np.arange(int(beat / 2 * 0.9 * sr)) / sr
            fq = midi_hz(root + (12 if j % 4 == 3 else 0))
            sig = (np.sin(2 * np.pi * fq * ll) + 0.4 * np.sin(4 * np.pi * fq * ll)) * np.exp(-ll / 0.18)
            add(int(st * sr), sig, 0.5, 0.09 * clamp((I - 0.25) / 0.5))
    # bumbo e chimbal
    st = 0.0
    while st < DUR - 1:
        I = intensity(st)
        kk = 0.32 * clamp((I - 0.5) / 0.5)
        if kk > 0:
            lt = np.arange(int(0.4 * sr)) / sr
            fq = 50 + 80 * np.exp(-lt / 0.03)
            add(int(st * sr), np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.exp(-lt / 0.14), 0.5, kk)
        hh = 0.06 * clamp((I - 0.35) / 0.5)
        if hh > 0:
            nz = rng.standard_normal(int(0.05 * sr))
            nz = (nz - _lowpass(nz, 4)) * np.exp(-np.arange(len(nz)) / sr / 0.012)
            add(int((st + beat / 2) * sr), nz, 0.65, hh)
        st += beat
    # tique-taque dos 7 dias e relógio do backup
    for t0, t1, step in [(25.0, 38.0, 0.5), (44.0, 49.0, 0.125)]:
        st = t0
        k = 0
        while st < t1:
            lt = np.arange(int(0.03 * sr)) / sr
            fq = 2400 if k % 2 == 0 else 1900
            add(int(st * sr), np.sin(2 * np.pi * fq * lt) * np.exp(-lt / 0.006), 0.4 + 0.2 * (k % 2), 0.09)
            st += step
            k += 1
    # arpejo rápido durante o trabalho do backup
    st = 42.5
    k = 0
    arp = [62, 65, 69, 74, 77, 74, 69, 65]
    while st < 50.5:
        lt = np.arange(int(0.25 * sr)) / sr
        fq = midi_hz(arp[k % 8] + 12)
        add(int(st * sr), np.sin(2 * np.pi * fq * lt) * np.exp(-lt / 0.08), 0.3 + 0.4 * (k % 2), 0.05)
        st += beat / 4
        k += 1

    def impact(t0, gain):
        lt = np.arange(int(2.5 * sr)) / sr
        fq = 38 + 60 * np.exp(-lt / 0.08)
        boom = np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.exp(-lt / 0.7)
        nz = _lowpass(rng.standard_normal(len(lt)), 8) * np.exp(-lt / 0.25)
        add(int(t0 * sr), boom + 0.5 * nz, 0.5, gain)

    def riser(t1, ln, gain):
        lt = np.arange(int(ln * sr)) / sr
        nz = rng.standard_normal(len(lt))
        nz = _lowpass(nz, 5) - _lowpass(nz, 40)
        add(int((t1 - ln) * sr), nz * (lt / ln) ** 2.5, 0.5, gain)

    riser(3.0, 2.2, 0.08)
    impact(3.0, 0.3)
    riser(71.0, 3.0, 0.1)
    impact(71.0, 0.4)
    impact(82.7, 0.22)
    impact(89.0, 0.25)
    impact(153.6, 0.3)
    for tc in CORTES:
        ln = int(1.4 * sr)
        lt = np.arange(ln) / sr
        nz = _lowpass(rng.standard_normal(ln), 25)
        add(int((tc - 1.2) * sr), nz * (lt / 1.2) ** 2 * np.clip((1.4 - lt) / 0.2, 0, 1), 0.5, 0.15)
    ir_len = int(2.0 * sr)
    it = np.arange(ir_len) / sr
    nfft = 1 << int(math.ceil(math.log2(n + ir_len)))
    out = []
    for sig, seed in [(L, 61), (R, 62)]:
        ir = np.random.default_rng(seed).standard_normal(ir_len) * np.exp(-it / 0.5)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(sig, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]
        out.append(sig * 0.85 + wet * 0.3)
    L, R = out
    fade = np.clip(tt / 0.8, 0, 1) * np.clip((DUR - tt) / 3.0, 0, 1)
    stereo = np.stack([L * fade, R * fade], axis=1)
    stereo *= 10 ** (-17 / 20) / np.sqrt(np.mean(stereo ** 2))
    lim = 10 ** (-2.5 / 20)
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
    ap.add_argument("--poster-t", type=float, default=74.0)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()
    langs = args.lang or list(TXT)
    if args.stills:
        os.makedirs(args.stills_dir, exist_ok=True)
        for lang in langs:
            for t in args.stills:
                draw(t, TXT[lang]).save(os.path.join(args.stills_dir, f"{lang}_{t:05.1f}.png"))
        return
    with tempfile.TemporaryDirectory(prefix="iotedu_") as tmp:
        wav = os.path.join(tmp, "trilha.wav")
        print("trilha...", flush=True)
        soundtrack(wav)
        for lang in langs:
            render(lang, wav, args.outdir, args.poster_t, args.jobs)


if __name__ == "__main__":
    main()
