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

---

# Clipe "Kauã e o poder de criar" (fábula)

Fábula de 2 min 54 s (1280x720, 30 fps, H.264 + AAC, cerca de 9,5 MB por idioma): um jovem indígena no coração da Amazônia ganha internet via satélite, um notebook e acesso a um modelo de IA (Claude), cria um produto para a floresta que vira sucesso internacional e investe o dinheiro na aldeia. Moral: internet e IA democratizam o poder de criar. Personagem e produto são fictícios, e o clipe diz isso no fim.

Diferente dos outros clipes, o estilo é de ilustração plana (formas preenchidas, sem o brilho neon), mas com as mesmas fontes, cores de destaque e logo. Os textos são desenhados no quadro, então há uma versão por idioma. A trilha é própria: Am–F–C–G a 90 bpm, marimba pentatônica, sons da mata (vento, pássaros, grilos), motosserra e avisos sintetizados.

```sh
python3 -I tools/clipe/render_kaua.py                 # pt, en e es (cerca de 3 minutos com 16 núcleos)
python3 -I tools/clipe/render_kaua.py --lang en       # só um idioma
python3 -I tools/clipe/render_kaua.py --stills 21 58 101 --stills-dir /tmp/quadros
```

Gera `assets/video/kaua-ia.mp4` (pt), `kaua-ia.en.mp4` e `kaua-ia.es.mp4`, cada um com o pôster `.jpg` (quadro de 58 s). Os quadros são desenhados em paralelo (`--jobs`, padrão: núcleos menos 2).

## Cenas

1. **0–8 s, abertura:** mata à noite com vaga-lumes; "Kauã e o poder de criar", "Uma fábula sobre internet, IA e transformação".
2. **8–30 s, a mata (a):** amanhecer na aldeia; Kauã chega caminhando. Fumaça e motosserra ao longe: a floresta está em perigo. "Sem sinal": a aldeia está desconectada.
3. **30–50 s, a antena (b):** Kauã e um ancião montam uma antena de internet via satélite (como a Starlink); anoitece, um trem de satélites cruza o céu, o feixe chega à antena e o Wi-Fi cobre a aldeia. "ONLINE".
4. **50–64 s, o notebook (c):** um projeto de inclusão digital entrega uma caixa; o notebook acende; Kauã, sentado perto da fogueira, começa a usar.
5. **64–96 s, a IA (d):** tela do chat com o Claude. Kauã, que não é programador, pergunta como proteger a mata; a IA propõe sensores com celulares usados e painel solar e um modelo que reconhece motosserra e fogo; aparece o código e o teste do modelo (motosserra 97%).
6. **96–110 s, o produto (e):** o Kaá Sentinela (kaá: mata, em tupi) escuta a mata à noite; um sensor detecta a motosserra, o alerta salta de árvore em árvore até a aldeia, e os guardiões saem com lanternas. "Floresta protegida".
7. **110–128 s, o sucesso:** globo com arcos para 12 países, contadores (38 países, 1.200 comunidades, R$ 12,4 milhões) e manchetes em quatro idiomas; Kauã comemora.
8. **128–146 s, a aldeia nova:** painéis solares, caixa d'água, posto de saúde e crianças com notebooks na escola conectada.
9. **146–174 s, a moral:** internet + notebook + IA = poder de criar; "Qualquer pessoa, em qualquer lugar…", "Criar soluções digitais não é mais privilégio…", "Criar soluções para problemas locais pode ser o grande diferencial"; encerramento com "Internet e IA democratizam o poder de criar", logo, data e local.

---

# Clipe "A revolução da IA já começou. E está atropelando" (caso real IoTEdu)

Clipe de 2 min 46 s (1280x720, 30 fps, H.264 + AAC, cerca de 5 MB por idioma) sobre um caso real do projeto de inovação IoTEdu (https://iotedu.org), relatado por Diego Kreutz (UNIPAMPA), coordenador do projeto. Uma equipe de 6 alunos levou 7 dias (cerca de 256 horas-pessoa) numa tarefa; um único aluno de graduação, usando LLMs em alto nível, entregou o mesmo resultado, melhor e mais completo, em 2 horas. Os números e as frases seguem o relato original; os alunos não são identificados (as figuras são genéricas).

Usa o motor de desenho do clipe da fábula (`render_kaua.py`: classe `Cv`, `person`, `caption`, `logo`), com fundo escuro quadriculado. Trilha própria: Dm–B♭–F–C a 112 bpm, baixo em colcheias, tique-taque nos 7 dias e no relógio de 2 horas, e impactos no 128×.

```sh
python3 -I tools/clipe/render_iotedu.py                 # pt, en e es
python3 -I tools/clipe/render_iotedu.py --lang en       # só um idioma
python3 -I tools/clipe/render_iotedu.py --stills 30 72 --stills-dir /tmp/quadros
```

Gera `assets/video/revolucao-ia.mp4` (pt), `revolucao-ia.en.mp4` e `revolucao-ia.es.mp4`, cada um com o pôster `.jpg` (quadro de 74 s, o "128×").

## Cenas

1. **0–7,5 s, abertura:** rajadas de luz atravessam a tela; "A revolução da IA já começou. E está atropelando."; "Uma história real · projeto de inovação IoTEdu · UNIPAMPA".
2. **7,5–20 s, o fato:** "Não é hipótese, não é projeção, não é hype" (riscados). "É medição."
3. **20–40 s, a equipe:** 6 alunos (2 de graduação, 3 de mestrado, 1 mestre) com notebooks; calendário de 7 dias, contador até 256 horas-pessoa e barra de entrega.
4. **40–58 s, o backup:** um aluno de graduação com LLMs; relógio de 2 horas; a barra enche e passa do fim: "melhor e mais completo".
5. **58–78 s, a matemática que dói:** barras de 256 horas-pessoa e de 2 horas em escala; 256 ÷ 2 = 128×.
6. **78–100 s, a narrativa confortável:** a mensagem "sênior +80%, júnior −20%" recebe o carimbo "ERRADA"; gráfico 0,8× / 1,8× / 128×. "A IA não nivela. A IA amplia o gap."
7. **100–110 s, o diferencial:** resolver problemas + experiência em projetos reais + domínio da IA = velocidade sem precedentes.
8. **110–122 s, implicações para o ensino:** currículo, avaliações, critérios de um bom aluno, formação, relevância da sala de aula.
9. **122–134 s, recado para as empresas:** proibir juniores de usar IA é um erro estratégico grave.
10. **134–152 s, recado para os professores:** as três perguntas.
11. **152–166 s, encerramento:** curvas que se afastam (o gap), a frase final, crédito do relato e marca do Summit.

---

# Versões narradas de todos os clipes

Cada clipe tem também uma versão narrada, em português, inglês e espanhol, com trilha nova. As versões originais continuam no site e no repositório, sem alteração; as narradas têm `-narrado` no nome (por exemplo, `cowmed-ia-narrado.en.mp4`).

```sh
python3 tools/clipe/render_narrado.py                          # todos os clipes, nos três idiomas
python3 tools/clipe/render_narrado.py --clipe kaua --lang pt    # um clipe, um idioma
python3 tools/clipe/render_narrado.py --checa                  # só confere se as falas cabem nas cenas
python3 tools/clipe/render_narrado.py --clipe iotedu --so-audio /tmp/mix   # só a mixagem, em WAV
python3 tools/clipe/render_narrado.py --clipe kaua --stills 10 40 --stills-dir /tmp/quadros
```

Requer, além de Pillow, numpy e ffmpeg, o scipy (filtros da trilha) e o edge-tts (voz), com acesso à rede na primeira vez: as falas ficam em cache em `tools/clipe/.cache_voz/` (fora do git). Neste Mac, rode sem o `-I`, porque numpy, scipy e edge-tts estão instalados no site-packages do usuário. O ffmpeg é procurado na variável `FFMPEG`, depois no PATH e, por fim, no pacote imageio-ffmpeg.

## Como funciona

- `voz.py`: narração com vozes neurais da Microsoft (edge-tts), masculinas e de timbre médio-grave, com o tom levemente baixado: Antonio (pt-BR), Andrew (en-US) e Tomás (es-AR, rioplatense, vizinho da fronteira). Corta silêncios das pontas e encurta pausas longas entre frases; se uma fala não cabe na janela da cena, ela é sintetizada de novo até 14% mais rápida, e o script avisa se ainda assim não couber.
- `trilha_summit.py`: trilha eletrônica moderna, no estilo dos eventos de tecnologia: pad de serras desafinadas com sidechain, arpejo em semicolcheias com eco pingue-pongue, baixo, bumbo, palmas, chimbais, risers e impactos nos cortes de cena. Um motivo de sino, sempre com notas do acorde, aparece em todos os clipes, como assinatura sonora do Summit. A energia de cada trecho segue níveis de 0 (só pad) a 4 (tudo, filtro aberto).
- `render_narrado.py`: roteiros de narração (tempos e textos nos três idiomas), tonalidade, andamento e níveis da trilha de cada clipe, e a mixagem: a trilha abaixa cerca de 11 dB sob a voz (com antecipação de 150 ms), e o resultado é normalizado em -16 LUFS.

| Clipe | Arquivos | Duração | Trilha |
|---|---|---|---|
| IA + Inovação | `ia-inovacao-simbiose-narrado{,.en,.es}.mp4` | 72 s | Dm9–B♭maj7–F–Csus, 110 bpm |
| Cowmed | `cowmed-ia-narrado{,.en,.es}.mp4` | 75 s | G–D6–Em7–Cmaj7, 104 bpm |
| Chamada (4:5) | `alegrete-summit-2026-narrado{,.en,.es}.mp4` | 50 s | Am9–Fmaj7–C–G6, 120 bpm |
| A revolução da IA | `revolucao-ia-narrado{,.en,.es}.mp4` | 2 min 46 s | Dm7–B♭maj7–F–Csus, 118 bpm |
| Kauã e o poder de criar | `kaua-ia-narrado{,.en,.es}.mp4` | 88 s | Am9–Fmaj7–C–G6, 96 bpm |

Nos quatro primeiros, a imagem é copiada do vídeo original sem recodificar: só o áudio muda. Em IA + Inovação e Cowmed, os textos na tela seguem em português, e a narração em inglês ou espanhol vem acompanhada das legendas `.vtt` de sempre.

## A fábula de Kauã em 88 s

A versão narrada da fábula é uma nova montagem das cenas originais (`KAUA_EDL` em `render_narrado.py`): cada trecho é um intervalo do clipe de 2 min 54 s, tocado na velocidade original ou acelerado (até 3× no trem de satélites), com fusões de 0,5 s entre trechos não contíguos. Ficam a chegada de Kauã, a floresta em perigo, a aldeia sem sinal, a antena e o ONLINE, o notebook, o chat com a IA e o teste do modelo, o Kaá Sentinela, o sucesso internacional, a aldeia nova, a equação internet + notebook + IA = poder de criar, a moral e o encerramento com o aviso de ficção. A narração repete as legendas da tela; a mixagem inclui a motosserra ao longe e o alerta do Kaá. Ao mexer na montagem, o script confere a duração e para se ela passar de 90 s.
