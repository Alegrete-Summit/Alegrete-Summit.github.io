#!/usr/bin/env python3
"""Monta as páginas do site a partir dos fragmentos em _paginas/.

Cada fragmento começa com um cabeçalho de metadados entre linhas '---':

    ---
    titulo: Programação
    descricao: Texto para buscadores e redes sociais.
    menu: programacao
    ---
    <section>...</section>

Uso: python3 tools/montar_site.py   (gera os .html na raiz do repositório)
"""
import html
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FRAG = RAIZ / "_paginas"

MENU = [
    ("inicio", "index.html", "Início", ""),
    ("programacao", "programacao.html", "Programação", ""),
    ("novidades", "novidades.html", "Novidades", ""),
    ("ia", "ia-ecossistemas.html", "IA e ecossistemas", "nav-ia"),
    ("pampa", "ia-no-pampa.html", "IA no Pampa", "nav-ia"),
    ("inovar", "inovar-com-ia.html", "Inovar com IA", "nav-ia"),
    ("clipe", "clipe.html", "Clipe", "nav-ia"),
]

LOGO = """<svg viewBox="0 0 100 100" aria-hidden="true">
  <path class="logo-stroke" d="M30 60 L50 22 L58 37"/>
  <path class="logo-stroke" d="M65 49 L80 77 L70 77"/>
  <path class="logo-stroke" d="M22 79 L52 70"/>
  <circle class="logo-node" cx="30" cy="60" r="6"/><circle class="logo-node" cx="58" cy="37" r="6"/>
  <circle class="logo-node" cx="65" cy="49" r="6"/><circle class="logo-node" cx="70" cy="77" r="6"/>
  <circle class="logo-node" cx="22" cy="79" r="6"/><circle class="logo-node" cx="52" cy="70" r="6"/>
</svg>"""

MODELO = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js")</script>
<title>{titulo_completo}</title>
<meta name="description" content="{descricao}">
<meta property="og:title" content="{titulo_completo}">
<meta property="og:description" content="{descricao}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:image" content="assets/img/2025/palco-principal.jpg">
<meta name="theme-color" content="#050706">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<a class="sr-only" href="#conteudo">Pular para o conteúdo</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Alegrete Summit 2026, página inicial">
      {logo}
      <span>Alegrete<small>Summit 2026</small></span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav" aria-label="Principal">
{menu}
    </nav>
  </div>
</header>
<main id="conteudo">
{corpo}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <a class="brand" href="index.html">{logo}<span>Alegrete<small>Summit 2026</small></span></a>
      <p style="margin-top:14px">Inovar é construir pontes. Entre pessoas, conhecimento, campo, cidade e futuro.</p>
      <p>29 e 30 de outubro de 2026<br>Auditório da Superintendência do Sicredi Essência<br>Av. Assis Brasil, 1395, Cidade Alta, Alegrete/RS</p>
    </div>
    <div>
      <h4>Evento</h4>
      <ul>
        <li><a href="programacao.html">Programação</a></li>
        <li><a href="programacao.html#dia30">Palco Geek</a></li>
        <li><a href="novidades.html">Novidades 2026</a></li>
        <li><a href="novidades.html#edicao-2025">Edição 2025</a></li>
        <li><a href="index.html#apoio">Realização e apoio</a></li>
      </ul>
    </div>
    <div>
      <h4>IA e inovação</h4>
      <ul>
        <li><a href="ia-ecossistemas.html">O papel da IA nos ecossistemas</a></li>
        <li><a href="ia-no-pampa.html">IA nos setores do Pampa</a></li>
        <li><a href="inovar-com-ia.html">Como inovar com IA</a></li>
        <li><a href="clipe.html">Clipe: a simbiose</a></li>
        <li><a href="https://www.instagram.com/alegretecidadeinovadora/" rel="noopener">Instagram @alegretecidadeinovadora</a></li>
      </ul>
    </div>
    <p class="fine">Realização: Ecossistema de Inovação Alegrete Cidade Inovadora. Evento gratuito, com certificação de participação. Conteúdo da programação extraído das publicações oficiais no Instagram; confira atualizações em <a href="https://www.instagram.com/alegretecidadeinovadora/" rel="noopener">@alegretecidadeinovadora</a>.</p>
  </div>
</footer>
<script src="assets/js/site.js"></script>
</body>
</html>
"""


def ler(caminho):
    texto = caminho.read_text(encoding="utf-8")
    _, cab, corpo = texto.split("---\n", 2)
    meta = {}
    for linha in cab.strip().splitlines():
        chave, valor = linha.split(":", 1)
        meta[chave.strip()] = valor.strip()
    return meta, corpo


def menu(ativo):
    linhas = []
    for chave, href, rotulo, classe in MENU:
        attrs = f' class="{classe}"' if classe else ""
        if chave == ativo:
            attrs += ' aria-current="page"'
        linhas.append(f'      <a href="{href}"{attrs}>{rotulo}</a>')
    return "\n".join(linhas)


def main():
    for chave, href, _, _ in MENU:
        meta, corpo = ler(FRAG / href)
        titulo = meta["titulo"]
        completo = "Alegrete Summit 2026" if chave == "inicio" else f"{titulo} · Alegrete Summit 2026"
        saida = MODELO.format(
            titulo_completo=html.escape(completo),
            descricao=html.escape(meta["descricao"]),
            logo=LOGO,
            menu=menu(chave),
            corpo=corpo.strip("\n"),
        )
        (RAIZ / href).write_text(saida, encoding="utf-8")
        print("gerado", href)


if __name__ == "__main__":
    main()
