# Clipe "IA + Inovação: a simbiose indissolúvel"

Clipe animado de 72 s (1280x720, 30 fps, H.264 + AAC) do Alegrete Summit 2026, gerado inteiramente por código: os quadros são desenhados com Pillow e a trilha é sintetizada com numpy. Não há imagens nem áudio de terceiros.

## Como gerar de novo

```sh
python3 -I tools/clipe/render_clipe.py
```

Gera `assets/video/ia-inovacao-simbiose.mp4` e o pôster `assets/video/ia-inovacao-simbiose.jpg` (quadro de 21 s) em cerca de 1 minuto. Requer Python 3 com Pillow e numpy, e o ffmpeg: o script usa a variável `FFMPEG`, depois o `ffmpeg` do PATH e, por fim, o binário do imageio-ffmpeg no cache do uv.

Para conferir só alguns quadros, sem gerar o vídeo:

```sh
python3 -I tools/clipe/render_clipe.py --stills 4.5 20 33 --stills-dir /tmp/quadros
```

## Cenas

1. **0–6 s, abertura:** linhas de circuito crescem dos cantos, o triângulo do logo se monta, "ALEGRETE SUMMIT 2026 apresenta".
2. **6–14,5 s, os dois organismos:** a rede neural verde (IA) e a forma orgânica âmbar (inovação: pessoas, ideias, território). "IA sem inovação perde o sentido." / "Inovação sem IA perde a velocidade."
3. **14,5–24 s, a simbiose:** as duas fitas se entrelaçam numa dupla hélice. "IA + INOVAÇÃO: a simbiose indissolúvel".
4. **24–40 s, o Pampa:** horizonte de coxilhas, sol baixo, umbu e lavouras de arroz; oito setores se acendem e se conectam (arroz e água, pecuária, energia, saúde, educação, gestão pública, comércio e serviços, logística de fronteira).
5. **40–52 s, o ciclo:** Dados → Modelos → Decisões → Pessoas → Novos problemas. "A IA aprende com dados. A inovação aprende com pessoas. Supervisão humana em cada volta."
6. **52–62 s, a ponte:** quatro pilares (poder público, empresas, academia, sociedade) sustentam uma ponte em arco. "Inovar é construir pontes. A IA é a nova ponte."
7. **62–72 s, encerramento:** logo, "IA + INOVAÇÃO, simbiose indissolúvel e necessária", data e local do evento.

## Identidade visual e fontes

Fundo preto, verde neon (#19F58C) para a IA e âmbar (#FFB547) para a inovação e o território. Fontes em `fonts/`: Russo One e Chakra Petch, ambas sob a SIL Open Font License.
