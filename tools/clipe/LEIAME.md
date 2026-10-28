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

---

# Clipe "Cowmed: a IA que escuta o rebanho"

Caso de sucesso de 75 s (1280x720, 30 fps, H.264 + AAC) sobre a Cowmed, startup de Santa Maria (RS) incubada na Pulsar, a incubadora tecnológica da UFSM. Mesma identidade visual e mesmas funções do clipe anterior (o script importa `render_clipe.py`); a trilha é própria, em tom maior e mais pastoral. Não usa a marca nem imagens da empresa: só o nome, escrito com as fontes do Summit.

```sh
python3 -I tools/clipe/render_cowmed.py
```

Gera `assets/video/cowmed-ia.mp4` e o pôster `assets/video/cowmed-ia.jpg` (quadro de 39,5 s). As legendas em inglês e espanhol estão em `assets/video/cowmed-ia.en.vtt` e `assets/video/cowmed-ia.es.vtt`; se mudar textos ou tempos no script, atualize-as.

## Cenas

1. **0–8 s, abertura:** "Casos de sucesso · IA no Brasil", "Cowmed: a IA que escuta o rebanho".
2. **8–18 s, origem:** Santa Maria (RS); nasceu como projeto de estudantes da UFSM; incubada e graduada na Pulsar (UFSM → Pulsar → Cowmed).
3. **18–30 s, o problema:** sem dados, o produtor depende de observar o rebanho; cio e doença percebidos tarde significam leite e dinheiro perdidos.
4. **30–46 s, a solução com IA:** coleira com 25 leituras por segundo (ruminação, alimentação, atividade, ofegância); dados na nuvem interpretados pela Vic, a IA própria da empresa; alerta no celular (cio, saúde, estresse térmico) antes dos sinais clínicos.
5. **46–56 s, validação (2022):** R$ 5,9 milhões de 547 investidores, recorde em equity crowdfunding no Brasil; 35 mil vacas em mais de 400 fazendas.
6. **56–66 s, escala (2026):** 100 mil animais monitorados; receita de cerca de R$ 18 milhões em 2025 (autodeclarado); Paraguai, Uruguai e México.
7. **66–75 s, a lição:** problema do campo + ciência da universidade + incubadora regional = IA que sai do Pampa para o mundo; Alegrete Summit 2026.

## Fontes

- UFSM, Inovatec, abril de 2026 (incubação e graduação na Pulsar; projeto de estudantes): https://www.ufsm.br/orgaos-suplementares/inovatec?p=4008
- Forbes Brasil, dezembro de 2022 (R$ 5,9 milhões, 547 investidores, recorde em equity crowdfunding, 35 mil vacas, mais de 400 fazendas): https://forbes.com.br/forbes-agro/2022/12/startup-que-faz-vacas-falarem-capta-r-59-milhoes/
- CNN Brasil, 2026 (100 mil animais, receita de cerca de R$ 18 milhões em 2025, informada pela empresa; Paraguai, Uruguai e México): https://www.cnnbrasil.com.br/agro/cowmed-preve-salto-de-65-no-faturamento-com-vendas-de-coleiras-na-pecuaria/

O ano de fundação foi omitido de propósito: a UFSM cita o projeto desde 2010 e a Forbes cita 2019. O mapa da cena 6 é estilizado, não cartográfico.

---

# Clipe-chamada "Alegrete Summit 2026" (destaque da página inicial)

Chamada de 50 s, vertical 4:5 (720x900, 30 fps, H.264 + AAC), feita para o público-alvo do evento: por que participar, o que acontece nos dois dias e como o Summit conecta ideias, pessoas e negócios. O formato cabe no destaque da página inicial e no feed do Instagram. Os textos são desenhados no quadro, então há uma versão por idioma. Usa fotos da edição de 2025 (`assets/img/2025/`), recortadas para tirar os textos das artes, com a mesma identidade e as mesmas funções dos outros clipes (o script importa `render_clipe.py`). A trilha é própria: tom maior, 112 bpm, mais animada.

```sh
python3 -I tools/clipe/render_chamada.py              # pt, en e es (cerca de 2 minutos)
python3 -I tools/clipe/render_chamada.py --lang en    # só um idioma
python3 -I tools/clipe/render_chamada.py --stills 10 25 47 --stills-dir /tmp/quadros
```

Gera `assets/video/alegrete-summit-2026.mp4` (pt), `alegrete-summit-2026.en.mp4` e `alegrete-summit-2026.es.mp4`, cada um com o pôster `.jpg` (quadro de 47 s, com data, local e pré-inscrição). Na página inicial, o vídeo toca sem som e em loop, com botões para pausar e ativar o som; quem prefere menos movimento (`prefers-reduced-motion`) vê só o pôster.

## Cenas

1. **0–5,5 s, abertura:** logo, "ALEGRETE SUMMIT 2026", 29 e 30 de outubro, Alegrete/RS.
2. **5,5–12,5 s, o gancho:** "Tem uma ideia? Um projeto, um negócio, uma pesquisa? A conexão que falta pode estar no Summit."
3. **12,5–20,5 s, por que participar:** "Inovar é construir pontes": ponte em arco com pulsos nos dois sentidos, ligando quem produz e quem pesquisa, quem empreende e quem investe, o campo e a cidade.
4. **20,5–31,5 s, o que te espera:** 18 conversas no Palco Geek, 13 equipes no Bye Bye Boss, 1 dia de Ideathon, 2 dias de Mostra Tecnológica (fotos de 2025).
5. **31,5–38,5 s, conexões viram negócios:** rede de pessoas que se liga, e três ligações viram negócio. "Ideias encontram parceiros. Conexões viram negócios."
6. **38,5–42,5 s, para quem é:** estudantes, pesquisadores, empreendedores, investidores, produtores rurais, gestores públicos. "Para você."
7. **42,5–50 s, convite:** data, local, gratuito, certificado de 24 h, "Inovar é construir pontes", pré-inscrição no @alegretecidadeinovadora.
