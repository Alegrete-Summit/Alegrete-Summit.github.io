"""Trilha eletrônica dos clipes narrados do Alegrete Summit 2026.

Synthpop/eletrônica moderna, do tipo que se ouve em eventos de tecnologia:
pad de serras desafinadas com sidechain, arpejo em semicolcheias com eco
pingue-pongue, baixo, bateria (bumbo, palmas, chimbais), risers e impactos
nos cortes de cena, e um motivo de sino que se repete em todos os clipes,
como assinatura sonora do Summit. Tudo sintetizado com numpy e scipy.

A energia segue os níveis de cada clipe (0 a 4):
    0  pad e sinos esparsos         2  + baixo, chimbal e bumbo leve
    1  + arpejo filtrado            3  + bumbo 4/4, palmas e motivo
                                    4  + chimbal aberto e filtro todo aberto
"""
import math

import numpy as np
from scipy import signal

SR = 48000

# acordes: (fundamental MIDI, intervalos)
MENOR7 = [0, 3, 7, 10]
MAIOR7 = [0, 4, 7, 11]
ADD9 = [0, 4, 7, 14]
SUS = [0, 5, 7, 10]
MAIOR6 = [0, 4, 7, 9]
MENOR9 = [0, 3, 7, 14]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def voicing(raiz, ints, lo=53, hi=77):
    """Notas do acorde, todas puxadas para a faixa [lo, hi]."""
    out = []
    for i in ints:
        m = raiz + i
        while m < lo:
            m += 12
        while m > hi:
            m -= 12
        out.append(m)
    return sorted(set(out))


def saw(fq, n, ph=0.0):
    """Serra simples (o filtro passa-baixas depois tira o excesso de agudos)."""
    p = (ph + np.cumsum(np.full(n, fq / SR))) % 1.0
    return 2.0 * p - 1.0


def lp_var(x, fc, ordem=2, bloco=512):
    """Passa-baixas com corte variável no tempo (fc: vetor do tamanho de x)."""
    y = np.empty_like(x)
    zi = None
    for i0 in range(0, len(x), bloco):
        i1 = min(len(x), i0 + bloco)
        f = float(np.clip(fc[i0], 40, SR * 0.45))
        sos = signal.butter(ordem, f, "low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        y[i0:i1], zi = signal.sosfilt(sos, x[i0:i1], zi=zi)
    return y


def filtro(x, kind, fc, ordem=2):
    return signal.sosfilt(signal.butter(ordem, fc, kind, fs=SR, output="sos"), x)


def reverb_ir(seg=2.4, seed=3, brilho=5200):
    rng = np.random.default_rng(seed)
    n = int(seg * SR)
    t = np.arange(n) / SR
    env = np.exp(-t / (seg / 6.5)) * np.clip(t / 0.012, 0, 1)
    irs = []
    for _ in range(2):
        nz = filtro(rng.standard_normal(n), "low", brilho) * env
        irs.append(nz / np.sqrt(np.sum(nz ** 2)))
    return irs


class Trilha:
    def __init__(self, dur, bpm, prog, niveis, cortes=(), tom=None, seed=11, brilho=1.0, swing=0.0):
        """prog: um acorde por compasso; niveis: [(t, nível)]; cortes: tempos de impacto."""
        self.dur = dur
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.bar = 4 * self.beat
        self.prog = prog
        self.niveis = sorted(niveis)
        self.cortes = sorted(cortes)
        self.tom = tom if tom is not None else prog[0][0]
        self.rng = np.random.default_rng(seed)
        self.brilho = brilho
        self.swing = swing
        self.n = int((dur + 3.0) * SR)
        self.buses = {}

    # -------------------------------------------------------------- base

    def nivel(self, t):
        xs, ys = zip(*self.niveis)
        return float(np.interp(t, xs, ys, left=ys[0], right=ys[-1]))

    def nivel_degrau(self, t):
        """Nível vigente no tempo t (sem interpolar), quantizado no tempo musical."""
        v = self.niveis[0][1]
        for t0, lv in self.niveis:
            if t0 <= t + 1e-6:
                v = lv
        return v

    def bus(self, nome):
        if nome not in self.buses:
            self.buses[nome] = np.zeros((2, self.n))
        return self.buses[nome]

    def add(self, nome, t0, sig, pan=0.5, gain=1.0):
        b = self.bus(nome)
        i0 = int(round(t0 * SR))
        if sig.ndim == 1:
            sig = np.vstack([sig * math.cos(pan * math.pi / 2), sig * math.sin(pan * math.pi / 2)]) * math.sqrt(2)
        if i0 < 0:
            sig = sig[:, -i0:]
            i0 = 0
        i1 = min(self.n, i0 + sig.shape[1])
        if i1 > i0:
            b[:, i0:i1] += sig[:, : i1 - i0] * gain

    def acorde(self, t):
        return self.prog[int(max(0.0, t) // self.bar) % len(self.prog)]

    def curva(self, fn, passo=0.01):
        """Vetor por amostra a partir de fn(t), avaliada a cada passo s."""
        ts = np.arange(0, self.n / SR + passo, passo)
        vs = np.array([fn(t) for t in ts])
        return np.interp(np.arange(self.n) / SR, ts, vs)

    def pump(self, profundidade=0.55):
        """Ganho de sidechain: afunda a cada bumbo e volta em ~1/4 de tempo."""
        g = np.ones(self.n)
        rel = self.beat * 0.55
        ln = int(rel * SR)
        tt = np.arange(ln) / SR
        forma = 1 - profundidade * np.exp(-tt / (rel / 3.2)) * np.clip(tt / 0.004, 0, 1)
        for tk in self.kicks:
            i0 = int(tk * SR)
            i1 = min(self.n, i0 + ln)
            g[i0:i1] = np.minimum(g[i0:i1], forma[: i1 - i0])
        return g

    # ---------------------------------------------------------- camadas

    def tempos(self, sub):
        """Grade de tempos (sub = divisões por tempo) do início ao fim."""
        passo = self.beat / sub
        k = np.arange(int(self.dur / passo) + 2)
        ts = k * passo
        if self.swing and sub >= 2:
            ts = ts + np.where(k % 2 == 1, self.swing * passo, 0.0)
        return ts

    def bateria(self):
        self.kicks = []
        rng = self.rng
        for i, tb in enumerate(self.tempos(1)):
            if tb > self.dur - 0.3:
                break
            lv = self.nivel_degrau(tb)
            beat_in_bar = i % 4
            if lv >= 3 or (lv >= 2 and beat_in_bar in (0, 2)):
                self.kick(tb, 1.0 if lv >= 3 else 0.7)
                self.kicks.append(tb)
            if lv >= 3 and beat_in_bar in (1, 3):
                self.clap(tb, 0.9)
        for j, th in enumerate(self.tempos(4)):
            if th > self.dur - 0.3:
                break
            lv = self.nivel_degrau(th)
            pos = j % 4
            if lv >= 2 and (pos == 2 or (lv >= 3 and pos in (1, 3)) or (lv >= 4 and pos == 0)):
                vel = {0: 0.55, 1: 0.45, 2: 0.9, 3: 0.5}[pos] * (0.85 + 0.3 * rng.random())
                self.hat(th, vel, aberto=(lv >= 4 and pos == 2 and (j // 4) % 2 == 1))
        # fill de caixa antes de cada corte com nível alto
        for tc in self.cortes:
            if self.nivel_degrau(tc - 0.1) >= 3:
                for k in range(4):
                    self.clap(tc - self.beat + k * self.beat / 4, 0.35 + 0.15 * k)

    def kick(self, t0, g):
        ln = int(0.42 * SR)
        tt = np.arange(ln) / SR
        fq = 46 + 110 * np.exp(-tt / 0.035)
        corpo = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-tt / 0.16)
        click = filtro(self.rng.standard_normal(ln), "high", 2500) * np.exp(-tt / 0.004) * 0.25
        self.add("drums", t0, np.tanh(1.6 * (corpo + click)), 0.5, 0.5 * g)

    def clap(self, t0, g):
        ln = int(0.32 * SR)
        tt = np.arange(ln) / SR
        nz = filtro(self.rng.standard_normal(ln), "band", [900, 5200])
        env = np.zeros(ln)
        for k, d in enumerate([0.0, 0.011, 0.022]):
            i = int(d * SR)
            env[i:] += np.exp(-(tt[: ln - i]) / (0.008 if k < 2 else 0.09))
        tom = np.sin(2 * np.pi * 185 * tt) * np.exp(-tt / 0.04) * 0.3
        sig = (nz * env + tom) * 0.4
        self.add("drums", t0, sig, 0.5, g)
        self.add("rev", t0, sig, 0.5, g * 0.35)

    def hat(self, t0, g, aberto=False):
        ln = int((0.32 if aberto else 0.06) * SR)
        tt = np.arange(ln) / SR
        nz = filtro(self.rng.standard_normal(ln), "high", 7200)
        sig = nz * np.exp(-tt / (0.09 if aberto else 0.014)) * 0.2
        self.add("drums", t0, sig, 0.62 if aberto else 0.38, g)

    def pad(self):
        b = self.bus("pad_raw")
        for k in range(int(self.dur / self.bar) + 2):
            t0 = k * self.bar
            raiz, ints = self.acorde(t0)
            notas = voicing(raiz, ints)
            ln = int((self.bar + 0.6) * SR)
            tt = np.arange(ln) / SR
            env = np.clip(tt / 0.25, 0, 1) * np.clip((ln / SR - tt) / 0.6, 0, 1)
            for m in notas:
                for det, pan in [(-0.11, 0.2), (0.0, 0.5), (0.11, 0.8)]:
                    fq = midi_hz(m + det)
                    s = saw(fq, ln, self.rng.random()) * env
                    self.add("pad_raw", t0 - 0.05, s, pan, 0.045)
            # sub do pad: fundamental uma oitava abaixo, macia
            sub = np.sin(2 * np.pi * midi_hz(raiz - 12 if raiz >= 48 else raiz) * tt) * env
            self.add("pad_raw", t0 - 0.05, sub, 0.5, 0.05)
        fc = self.curva(lambda t: (900 + 800 * self.nivel(t)) * self.brilho)
        for c in range(2):
            b[c] = lp_var(b[c], fc)

    def baixo(self):
        for k, t8 in enumerate(self.tempos(2)):
            if t8 > self.dur - 0.2:
                break
            lv = self.nivel_degrau(t8)
            if lv < 1:
                continue
            raiz, _ = self.acorde(t8)
            m = raiz
            while m >= 45:
                m -= 12
            while m < 33:
                m += 12
            if lv == 1:
                if k % 8:
                    continue
                ln = int(self.bar * SR)
                g = 0.5
            else:
                if lv < 3 and k % 2 == 0:
                    continue  # nível 2: só contratempos
                ln = int(self.beat / 2 * 0.92 * SR)
                g = 0.75 if k % 2 else 0.55
                if lv >= 4 and k % 8 == 7:
                    m += 12
            tt = np.arange(ln) / SR
            fq = midi_hz(m)
            env = np.clip(tt / 0.006, 0, 1) * np.clip((ln / SR - tt) / 0.02, 0, 1)
            corpo = filtro(saw(fq, ln), "low", 420 + 260 * min(lv, 4) * self.brilho) * 0.8
            sub = np.sin(2 * np.pi * fq * tt)
            self.add("bass", t8, (corpo + sub) * env, 0.5, 0.27 * g)

    def arpejo(self):
        padrao = [0, 1, 2, 3, 2, 1, 3, 4]
        for j, ts in enumerate(self.tempos(4)):
            if ts > self.dur - 0.4:
                break
            lv = self.nivel_degrau(ts)
            if lv < 1:
                continue
            if lv == 1 and j % 2:
                continue  # nível 1: colcheias
            raiz, ints = self.acorde(ts)
            notas = voicing(raiz, ints, 60, 84)
            notas = notas + [n + 12 for n in notas]
            m = notas[padrao[j % 8] % len(notas)]
            ln = int(0.32 * SR)
            tt = np.arange(ln) / SR
            fq = midi_hz(m)
            env = np.exp(-tt / 0.085) * np.clip(tt / 0.002, 0, 1)
            sq = np.sign(np.sin(2 * np.pi * fq * tt)) * 0.5
            sig = (saw(fq, ln) * 0.6 + sq) * env
            vel = 0.8 if j % 4 == 0 else 0.6
            self.add("arp_raw", ts, sig, 0.5, 0.05 * vel)
        b = self.bus("arp_raw")
        fc = self.curva(lambda t: (1400 + 1300 * self.nivel(t)) * self.brilho)
        for c in range(2):
            b[c] = lp_var(b[c], fc)
        # eco pingue-pongue de 3/16
        d = int(self.beat * 0.75 * SR)
        eco = np.zeros_like(b)
        fonte = b.sum(axis=0) * 0.5
        g = 0.42
        for k in range(1, 5):
            c = k % 2
            eco[c, k * d:] += fonte[: self.n - k * d] * g
            g *= 0.55
        self.buses["arp_eco"] = eco

    def sino(self, t0, m, g, ln=1.6):
        n = int(ln * SR)
        tt = np.arange(n) / SR
        fq = midi_hz(m)
        mod = np.sin(2 * np.pi * fq * 3.5 * tt) * 2.2 * np.exp(-tt / 0.35)
        sig = np.sin(2 * np.pi * fq * tt + mod) * np.exp(-tt / 0.55) * np.clip(tt / 0.003, 0, 1)
        sig += 0.35 * np.sin(2 * np.pi * fq * 2 * tt) * np.exp(-tt / 0.25)
        self.add("bell", t0, sig, 0.45 + 0.1 * self.rng.random(), g)
        self.add("rev", t0, sig, 0.5, g * 0.6)

    def motivo(self):
        """Motivo de 2 compassos, sempre com notas do acorde (assinatura dos clipes)."""
        ritmo = [(0.0, 2), (0.75, 3), (1.5, 4), (2.5, 3), (3.0, 2), (4.5, 1), (5.0, 2), (6.0, 0)]
        k = 0
        while k * self.bar < self.dur - self.bar:
            t0 = k * self.bar
            lv = self.nivel_degrau(t0 + 0.05)
            if lv >= 3 and k % 4 in (0, 2) or lv <= 0.5 and k % 4 == 0:
                for b, idx in ritmo:
                    tb = t0 + b * self.beat
                    if tb > self.dur - 1.0 or (lv <= 0.5 and b > 3):
                        continue
                    raiz, ints = self.acorde(tb)
                    notas = voicing(raiz, ints, 67, 88)
                    m = notas[idx % len(notas)] + (12 if idx >= len(notas) else 0)
                    self.sino(tb, m, 0.075 if lv >= 3 else 0.05)
                k += 2
            else:
                k += 1

    def efeitos(self):
        for tc in self.cortes:
            lv = self.nivel_degrau(tc + 0.05)
            # riser de ruído filtrado
            ln = 1.8
            n = int(ln * SR)
            tt = np.arange(n) / SR
            nz = self.rng.standard_normal(n)
            fc = 300 * (40 ** (tt / ln))
            rise = lp_var(nz, fc) * (tt / ln) ** 2 * 0.09
            self.add("fx", tc - ln, rise, 0.5, 0.6 + 0.15 * lv)
            # impacto: boom grave + ruído com cauda
            n = int(2.5 * SR)
            tt = np.arange(n) / SR
            boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-tt / 0.08)) / SR) * np.exp(-tt / 0.6)
            nz = filtro(self.rng.standard_normal(n), "low", 3000) * np.exp(-tt / 0.18) * 0.25
            self.add("fx", tc, np.tanh(1.4 * (boom + nz)), 0.5, 0.18 + 0.05 * lv)
            self.add("rev", tc, nz, 0.5, 0.3)

    # ------------------------------------------------------------ saída

    def render(self):
        self.bateria()
        self.pad()
        self.baixo()
        self.arpejo()
        self.motivo()
        self.efeitos()
        pump = self.pump()
        pad = self.buses.pop("pad_raw") * pump * 0.9
        bass = self.bus("bass") * pump
        arp = (self.buses.pop("arp_raw") + self.buses.pop("arp_eco") * 0.7) * (0.35 + 0.65 * pump)
        rev_in = self.bus("rev") + pad * 0.25 + arp * 0.3
        irs = reverb_ir()
        wet = np.vstack([signal.fftconvolve(rev_in[c], irs[c])[: self.n] for c in range(2)])
        mixv = pad + bass + arp + self.bus("drums") + self.bus("bell") + self.bus("fx") + wet * 0.28
        # entra e sai suave
        tt = np.arange(self.n) / SR
        mixv *= np.clip(tt / 0.4, 0, 1) * np.clip((self.dur - tt) / 1.6, 0, 1)
        mixv = np.tanh(mixv * 1.1) / 1.1
        pico = np.max(np.abs(mixv)) + 1e-9
        return (mixv / pico * 0.89)[:, : int(self.dur * SR)]
