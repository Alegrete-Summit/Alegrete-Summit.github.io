"""Narração dos clipes narrados: voz neural (edge-tts) com cache em disco.

Cada fala vira um vetor numpy mono de 48 kHz. As falas sintetizadas ficam em
tools/clipe/.cache_voz/ (fora do git), então gerar de novo não exige rede.
"""
import asyncio
import hashlib
import os
import shutil
import subprocess

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, ".cache_voz")
SR = 48000

# vozes masculinas, de timbre médio-grave e naturais; o tom é baixado de leve
VOZES = {
    "pt": ("pt-BR-AntonioNeural", "-3Hz"),
    "en": ("en-US-AndrewNeural", "-2Hz"),
    "es": ("es-AR-TomasNeural", "-3Hz"),
}


def ffmpeg_bin():
    env_ff = os.environ.get("FFMPEG")
    if env_ff:
        return env_ff
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


async def _sintetiza(texto, voz, rate, pitch, destino):
    import edge_tts
    await edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch).save(destino)


def decodifica(path, sr=SR):
    out = subprocess.run([ffmpeg_bin(), "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def apara(x, limiar=0.004):
    """Tira o silêncio do começo e do fim, com uma folga curta."""
    idx = np.nonzero(np.abs(x) > limiar)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(0.02 * SR))
    b = min(len(x), idx[-1] + int(0.08 * SR))
    return x[a:b]


def encurta_pausas(x, maximo=0.24, limiar=0.006):
    """Pausas internas mais longas que `maximo` s ficam com `maximo` s."""
    hop = int(0.01 * SR)
    m = len(x) // hop
    quieto = np.sqrt((x[: m * hop].reshape(m, hop) ** 2).mean(axis=1)) < limiar
    manter = np.ones(len(x), dtype=bool)
    lim = int(maximo / 0.01)
    i = 0
    while i < m:
        if quieto[i]:
            j = i
            while j < m and quieto[j]:
                j += 1
            if j - i > lim and i > 0 and j < m:
                corte0 = (i + lim // 2) * hop
                corte1 = (j - lim // 2) * hop
                manter[corte0:corte1] = False
            i = j
        else:
            i += 1
    return x[manter]


def fala(texto, lang, rate=0):
    """Áudio da fala (numpy, 48 kHz, mono); rate em % (ex.: 8 = 8% mais rápida)."""
    voz, pitch = VOZES[lang]
    rate_s = f"{rate:+d}%"
    chave = hashlib.sha1(f"{voz}|{rate_s}|{pitch}|{texto}".encode()).hexdigest()[:20]
    os.makedirs(CACHE, exist_ok=True)
    mp3 = os.path.join(CACHE, chave + ".mp3")
    if not os.path.exists(mp3):
        tmp = mp3 + ".tmp"
        for tentativa in range(4):
            try:
                asyncio.run(_sintetiza(texto, voz, rate_s, pitch, tmp))
                break
            except Exception:
                if tentativa == 3:
                    raise
        os.replace(tmp, mp3)
    return encurta_pausas(apara(decodifica(mp3)))


def cabe(texto, lang, janela, rate_max=14):
    """Fala que cabe na janela (s), acelerando até rate_max%; devolve (áudio, rate)."""
    rate = 0
    while True:
        x = fala(texto, lang, rate)
        if len(x) / SR <= janela or rate >= rate_max:
            return x, rate
        excesso = len(x) / SR / janela
        rate = min(rate_max, max(rate + 3, int(round((excesso - 1) * 100)) + 2))
