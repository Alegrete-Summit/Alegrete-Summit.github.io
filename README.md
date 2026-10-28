# Alegrete Summit 2026

Site do Alegrete Summit 2026 (29 e 30 de outubro, Sicredi Essência, Alegrete/RS), publicado pelo GitHub Pages.

## Páginas

- `index.html`: início, tema, destaques, edição 2025, local e apoio
- `programacao.html`: programação hora a hora dos dois dias, com o Palco Geek
- `novidades.html`: linha do tempo de 2026, Missão São Paulo e memória de 2025
- `ia-ecossistemas.html`, `ia-no-pampa.html`, `inovar-com-ia.html`: especial sobre IA e inovação
- `clipe.html`: clipe animado "IA + Inovação: a simbiose indissolúvel"

## Idiomas

O site está em português (raiz), inglês (`en/`) e espanhol (`es/`), com os mesmos nomes de arquivo nos três idiomas e seletor PT · EN · ES em todas as páginas. O clipe tem legendas em inglês e espanhol (`assets/video/*.vtt`).

## Como editar

Edite os fragmentos em `_paginas/pt/`, `_paginas/en/` e `_paginas/es/` (cabeçalho, menu, rodapé e textos comuns de cada idioma ficam em `tools/montar_site.py`) e gere os HTML:

    python3 tools/montar_site.py

Estilos em `assets/css/site.css`; imagens em `assets/img/` (extraídas do Instagram @alegretecidadeinovadora).
O clipe é gerado por `tools/clipe/render_clipe.py` (veja `tools/clipe/LEIAME.md`).
