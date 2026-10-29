#!/usr/bin/env python3
"""Monta as páginas do site, em três idiomas, a partir dos fragmentos em _paginas/.

    _paginas/pt/*.html  ->  raiz do site   (português, idioma principal)
    _paginas/en/*.html  ->  en/            (inglês)
    _paginas/es/*.html  ->  es/            (espanhol)

Cada fragmento começa com um cabeçalho de metadados entre linhas '---':

    ---
    titulo: Programação
    descricao: Texto para buscadores e redes sociais.
    menu: programacao
    ---
    <section>...</section>

Campos opcionais do cabeçalho, para páginas com estilos ou scripts próprios
(lista separada por vírgulas; nomes simples são procurados em assets/css/ ou
assets/js/, endereços https:// entram como estão):

    css: kaua.css
    js: jogo-kaua.js

Os fragmentos usam caminhos como se estivessem na raiz (assets/..., programacao.html);
nas versões em inglês e espanhol, os caminhos de assets/ e musicas/ ganham o prefixo ../.
Os três idiomas usam os mesmos nomes de arquivo, o que permite trocar de idioma
mantendo a página.

Uso: python3 tools/montar_site.py
"""
import html
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FRAG = RAIZ / "_paginas"

IDIOMAS = ["pt", "en", "es"]
PASTA = {"pt": "", "en": "en/", "es": "es/"}
HTML_LANG = {"pt": "pt-BR", "en": "en", "es": "es"}
OG_LOCALE = {"pt": "pt_BR", "en": "en_US", "es": "es_ES"}
NOME_IDIOMA = {"pt": "Português", "en": "English", "es": "Español"}
SIGLA = {"pt": "PT", "en": "EN", "es": "ES"}

PAGINAS = [
    # chave, arquivo, grupo (evento | ia)
    ("inicio", "index.html", "evento"),
    ("programacao", "programacao.html", "evento"),
    ("novidades", "novidades.html", "evento"),
    ("ia", "ia-ecossistemas.html", "ia"),
    ("pampa", "ia-no-pampa.html", "ia"),
    ("inovar", "inovar-com-ia.html", "ia"),
    ("casos", "casos-de-sucesso.html", "ia"),
    ("clipe", "clipe.html", "ia"),
    ("musicas", "musicas.html", "ia"),
    ("fabula", "fabula-kaua.html", "ia"),
    ("jogo", "jogo-kaua.html", "ia"),
    ("simbiose", "jogo/jogo-simbiose.html", "ia"),
]

# páginas autônomas (tela cheia, só em português), que entram no menu mas não são montadas a partir de _paginas/
AUTONOMAS = {"simbiose"}

# páginas fora do menu principal (o jogo é linkado da fábula e do rodapé) -> item do menu que fica destacado nelas
FORA_DO_MENU = {"jogo": "fabula"}

TEXTOS = {
    "pt": {
        "menu": {"inicio": "Início", "programacao": "Programação", "novidades": "Novidades", "musicas": "Músicas",
                 "ia": "IA e ecossistemas", "pampa": "IA no Pampa", "inovar": "Inovar com IA", "casos": "Casos de sucesso", "clipe": "Clipes",
                 "fabula": "A fábula de Kauã", "jogo": "Jogo: Kauã", "simbiose": "Jogo: Simbiose"},
        "pular": "Pular para o conteúdo", "home": "Alegrete Summit 2026, página inicial",
        "abrir": "Menu", "nav": "Principal", "idioma": "Idioma",
        "grupo_evento": "Evento", "grupo_ia": "IA e inovação",
        "lema": "Inovar é construir pontes. Entre pessoas, conhecimento, campo, cidade e futuro.",
        "quando": "29 e 30 de outubro de 2026<br>Auditório da Superintendência do Sicredi Essência<br>Av. Assis Brasil, 1395, Cidade Alta, Alegrete/RS",
        "rod_evento": [("programacao.html", "Programação"), ("programacao.html#dia30", "Palco Geek"),
                       ("novidades.html", "Novidades 2026"), ("novidades.html#edicao-2025", "Edição 2025"), ("musicas.html", "Músicas do Summit"),
                       ("index.html#apoio", "Realização e apoio")],
        "rod_ia": [("ia-ecossistemas.html", "O papel da IA nos ecossistemas"), ("ia-no-pampa.html", "IA nos setores do Pampa"),
                   ("inovar-com-ia.html", "Como inovar com IA"), ("casos-de-sucesso.html", "Startups brasileiras com IA"), ("clipe.html", "Clipe: a simbiose"),
                   ("fabula-kaua.html", "A fábula de Kauã"), ("jogo-kaua.html", "Jogo: Kauã e o Kaá Sentinela"), ("jogo/jogo-simbiose.html", "Jogo: Simbiose, IA vs IA")],
        "fino": "Realização: Ecossistema de Inovação Alegrete Cidade Inovadora. Evento gratuito, com certificação de participação. Programação extraída das publicações oficiais no Instagram; confira atualizações em",
        "topo": "Voltar ao topo",
    },
    "en": {
        "menu": {"inicio": "Home", "programacao": "Schedule", "novidades": "News", "musicas": "Music",
                 "ia": "AI & ecosystems", "pampa": "AI in the Pampa", "inovar": "Innovate with AI", "casos": "Success stories", "clipe": "Clips",
                 "fabula": "Kauã's fable", "jogo": "Game: Kauã", "simbiose": "Game: Symbiosis"},
        "pular": "Skip to content", "home": "Alegrete Summit 2026, home page",
        "abrir": "Menu", "nav": "Main", "idioma": "Language",
        "grupo_evento": "Event", "grupo_ia": "AI and innovation",
        "lema": "Innovating is building bridges. Between people, knowledge, countryside, city and future.",
        "quando": "October 29–30, 2026<br>Auditorium of the Sicredi Essência headquarters<br>Av. Assis Brasil, 1395, Cidade Alta, Alegrete, RS, Brazil",
        "rod_evento": [("programacao.html", "Schedule"), ("programacao.html#dia30", "Palco Geek"),
                       ("novidades.html", "2026 news"), ("novidades.html#edicao-2025", "2025 edition"), ("musicas.html", "Summit music"),
                       ("index.html#apoio", "Organizers and supporters")],
        "rod_ia": [("ia-ecossistemas.html", "The role of AI in ecosystems"), ("ia-no-pampa.html", "AI across the Pampa's sectors"),
                   ("inovar-com-ia.html", "How to innovate with AI"), ("casos-de-sucesso.html", "Brazilian AI startups"), ("clipe.html", "Clip: the symbiosis"),
                   ("fabula-kaua.html", "Kauã's fable"), ("jogo-kaua.html", "Game: Kauã and the Kaá Sentinel"), ("jogo/jogo-simbiose.html", "Game: Symbiosis, AI vs AI (in Portuguese)")],
        "fino": "Organized by the Alegrete Cidade Inovadora innovation ecosystem. Free event with a certificate of participation. Schedule taken from the official Instagram posts; check for updates at",
        "topo": "Back to top",
    },
    "es": {
        "menu": {"inicio": "Inicio", "programacao": "Programa", "novidades": "Novedades", "musicas": "Música",
                 "ia": "IA y ecosistemas", "pampa": "IA en el Pampa", "inovar": "Innovar con IA", "casos": "Casos de éxito", "clipe": "Clips",
                 "fabula": "La fábula de Kauã", "jogo": "Juego: Kauã", "simbiose": "Juego: Simbiosis"},
        "pular": "Saltar al contenido", "home": "Alegrete Summit 2026, página de inicio",
        "abrir": "Menú", "nav": "Principal", "idioma": "Idioma",
        "grupo_evento": "Evento", "grupo_ia": "IA e innovación",
        "lema": "Innovar es construir puentes. Entre personas, conocimiento, campo, ciudad y futuro.",
        "quando": "29 y 30 de octubre de 2026<br>Auditorio de la Superintendencia de Sicredi Essência<br>Av. Assis Brasil, 1395, Cidade Alta, Alegrete/RS, Brasil",
        "rod_evento": [("programacao.html", "Programa"), ("programacao.html#dia30", "Palco Geek"),
                       ("novidades.html", "Novedades 2026"), ("novidades.html#edicao-2025", "Edición 2025"), ("musicas.html", "Música del Summit"),
                       ("index.html#apoio", "Organización y apoyo")],
        "rod_ia": [("ia-ecossistemas.html", "El papel de la IA en los ecosistemas"), ("ia-no-pampa.html", "IA en los sectores del Pampa"),
                   ("inovar-com-ia.html", "Cómo innovar con IA"), ("casos-de-sucesso.html", "Startups brasileñas con IA"), ("clipe.html", "Clip: la simbiosis"),
                   ("fabula-kaua.html", "La fábula de Kauã"), ("jogo-kaua.html", "Juego: Kauã y el Kaá Centinela"), ("jogo/jogo-simbiose.html", "Juego: Simbiosis, IA vs IA (en portugués)")],
        "fino": "Organiza: Ecosistema de Innovación Alegrete Cidade Inovadora. Evento gratuito, con certificado de participación. Programa tomado de las publicaciones oficiales en Instagram; consulta las novedades en",
        "topo": "Volver arriba",
    },
}

LOGO = """<svg viewBox="0 0 100 100" aria-hidden="true">
  <path class="logo-stroke" d="M30 60 L50 22 L58 37"/>
  <path class="logo-stroke" d="M65 49 L80 77 L70 77"/>
  <path class="logo-stroke" d="M22 79 L52 70"/>
  <circle class="logo-node" cx="30" cy="60" r="6"/><circle class="logo-node" cx="58" cy="37" r="6"/>
  <circle class="logo-node" cx="65" cy="49" r="6"/><circle class="logo-node" cx="70" cy="77" r="6"/>
  <circle class="logo-node" cx="22" cy="79" r="6"/><circle class="logo-node" cx="52" cy="70" r="6"/>
</svg>"""

MODELO = """<!doctype html><html lang="{html_lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<script>document.documentElement.classList.add("js")</script>
<title>{titulo_completo}</title>
<meta name="description" content="{descricao}">
<meta property="og:title" content="{titulo_completo}">
<meta property="og:description" content="{descricao}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{og_locale}">
<meta property="og:image" content="{base}assets/img/2025/palco-principal.jpg">
<meta name="theme-color" content="#050706">
{alternates}
<link rel="icon" href="{base}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/site.css">
{estilos_extras}</head>
<body>
<a class="skip" href="#conteudo">{t_pular}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="{t_home}">
      {logo}
      <span>Alegrete<small>Summit 2026</small></span>
    </a>
    <nav class="nav" id="nav" aria-label="{t_nav}">
{menu}
    </nav>
    <div class="lang" role="group" aria-label="{t_idioma}">
{idiomas}
    </div>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav"><span class="burger" aria-hidden="true"></span><span class="nav-toggle-label">{t_abrir}</span></button>
  </div>
</header>
<main id="conteudo">
{corpo}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <a class="brand" href="index.html">{logo}<span>Alegrete<small>Summit 2026</small></span></a>
      <p style="margin-top:14px">{t_lema}</p>
      <p>{t_quando}</p>
    </div>
    <div>
      <h4>{t_grupo_evento}</h4>
      <ul>
{rod_evento}
      </ul>
    </div>
    <div>
      <h4>{t_grupo_ia}</h4>
      <ul>
{rod_ia}
        <li><a href="https://www.instagram.com/alegretecidadeinovadora/" rel="noopener">Instagram @alegretecidadeinovadora</a></li>
      </ul>
    </div>
    <div class="fine">
      <p>{t_fino} <a href="https://www.instagram.com/alegretecidadeinovadora/" rel="noopener">@alegretecidadeinovadora</a>.</p>
      <p class="lang-foot">{idiomas_rodape} · <a href="#conteudo">{t_topo} ↑</a></p>
    </div>
  </div>
</footer>
<script src="{base}assets/js/site.js"></script>
{scripts_extras}</body>
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


def caminho_para(origem, destino, arquivo):
    """Caminho relativo da página no idioma `origem` até `arquivo` no idioma `destino`."""
    subir = "../" if PASTA[origem] else ""
    return subir + PASTA[destino] + arquivo


def menu(lang, ativo, base):
    t = TEXTOS[lang]["menu"]
    linhas = []
    ativo = FORA_DO_MENU.get(ativo, ativo)
    for chave, arquivo, grupo in PAGINAS:
        if chave in FORA_DO_MENU:
            continue
        attrs = ' class="nav-ia"' if grupo == "ia" else ""
        if chave == ativo:
            attrs += ' aria-current="page"'
        if chave in AUTONOMAS:
            arquivo = base + arquivo
        linhas.append(f'      <a href="{arquivo}"{attrs}>{t[chave]}</a>')
    return "\n".join(linhas)


def seletor(lang, arquivo, curto=True):
    itens = []
    for outro in IDIOMAS:
        rotulo = SIGLA[outro] if curto else NOME_IDIOMA[outro]
        href = caminho_para(lang, outro, arquivo)
        atual = ' aria-current="true"' if outro == lang else ""
        itens.append(f'      <a href="{href}" hreflang="{HTML_LANG[outro]}" lang="{HTML_LANG[outro]}" '
                     f'title="{NOME_IDIOMA[outro]}"{atual}>{rotulo}</a>')
    return ("\n" if curto else " · ").join(i.strip() if not curto else i for i in itens)


def alternates(lang, arquivo):
    linhas = [f'<link rel="alternate" hreflang="{HTML_LANG[o]}" href="{caminho_para(lang, o, arquivo)}">' for o in IDIOMAS]
    linhas.append(f'<link rel="alternate" hreflang="x-default" href="{caminho_para(lang, "pt", arquivo)}">')
    return "\n".join(linhas)


def lista(itens, base):
    autonomos = {a for c, a, _ in PAGINAS if c in AUTONOMAS}
    return "\n".join(f'        <li><a href="{base + h if h in autonomos else h}">{r}</a></li>' for h, r in itens)


def extras(meta, campo, base):
    """Tags <link>/<script> para os campos opcionais `css` e `js` do cabeçalho."""
    itens = [i.strip() for i in meta.get(campo, "").split(",") if i.strip()]
    tags = []
    for item in itens:
        url = item if item.startswith("https://") else f"{base}assets/{campo}/{item}"
        url = html.escape(url)
        tags.append(f'<link rel="stylesheet" href="{url}">' if campo == "css" else f'<script src="{url}"></script>')
    return "".join(t + "\n" for t in tags)


def main():
    for lang in IDIOMAS:
        base = "../" if PASTA[lang] else ""
        t = TEXTOS[lang]
        (RAIZ / PASTA[lang]).mkdir(exist_ok=True)
        for chave, arquivo, _ in PAGINAS:
            if chave in AUTONOMAS:
                continue
            fonte = FRAG / lang / arquivo
            if not fonte.exists():
                print("faltando", fonte.relative_to(RAIZ))
                continue
            meta, corpo = ler(fonte)
            if base:
                corpo = re.sub(r'((?:src|href|poster)=")(assets|musicas)/', r"\1" + base + r"\2/", corpo)
            titulo = meta["titulo"]
            completo = "Alegrete Summit 2026" if chave == "inicio" else f"{titulo} · Alegrete Summit 2026"
            saida = MODELO.format(
                html_lang=HTML_LANG[lang], og_locale=OG_LOCALE[lang], base=base,
                titulo_completo=html.escape(completo), descricao=html.escape(meta["descricao"]),
                alternates=alternates(lang, arquivo), logo=LOGO,
                menu=menu(lang, chave, base), idiomas=seletor(lang, arquivo),
                idiomas_rodape=seletor(lang, arquivo, curto=False),
                rod_evento=lista(t["rod_evento"], base), rod_ia=lista(t["rod_ia"], base),
                corpo=corpo.strip("\n"),
                estilos_extras=extras(meta, "css", base), scripts_extras=extras(meta, "js", base),
                **{"t_" + k: v for k, v in t.items() if isinstance(v, str)},
            )
            (RAIZ / PASTA[lang] / arquivo).write_text(saida, encoding="utf-8")
            print("gerado", PASTA[lang] + arquivo)


if __name__ == "__main__":
    main()
