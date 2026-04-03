"""Generate activismo-quercus.html from extracted HTML-formatted JSON data."""

import json
import sys
import html
import re
import os
from collections import defaultdict

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)

SITE = r"C:\Users\quent\Downloads\Claude\CV"

with open(
    os.path.join(SITE, "data", "quercus_comunicados_html.json"), "r", encoding="utf-8"
) as f:
    comunicados = json.load(f)

with open(
    os.path.join(SITE, "data", "quercus_paginas_html.json"), "r", encoding="utf-8"
) as f:
    paginas = json.load(f)


# --- Categorization ---
def categorize(title, content):
    t = (title + " " + content[:500]).lower()
    if any(
        w in t
        for w in [
            "co-inciner",
            "resíduo",
            "reciclagem",
            "aterro",
            "embalage",
            "pilha",
            "óleos usados",
            "pneus usados",
            "lixo",
            "hospitalar",
        ]
    ):
        return "Resíduos e Reciclagem"
    if any(
        w in t
        for w in [
            "transgénico",
            "geneticamente modificado",
            "ogm",
            "dioxina",
            "alimento contaminad",
            "biosegurança",
            "bio(in)segurança",
        ]
    ):
        return "Alimentação e OGM"
    if any(
        w in t
        for w in [
            "alteraç",
            "climátic",
            "quioto",
            "kyoto",
            "marraque",
            "haia",
            "emissõ",
            "ozono",
            "co2",
            "carbono",
            "energia",
        ]
    ):
        return "Energia e Clima"
    if any(
        w in t
        for w in [
            "transport",
            "aeroporto",
            "ponte 25",
            "comboio",
            "combóio",
            "portag",
            "carris",
            "eléctric",
            "sem carro",
            "veículo",
            "automóv",
            "aviação",
            "mtbe",
            "gasolina",
            "gasóleo",
        ]
    ):
        return "Transportes e Mobilidade"
    if any(
        w in t
        for w in [
            "floresta",
            "eucalipt",
            "sobreir",
            "montado",
            "cortiça",
            "fogo",
            "incêndio",
            "arrase de vegetação",
        ]
    ):
        return "Floresta"
    if any(w in t for w in ["caça", "caca", "venatór", "não caça"]):
        return "Conservação da Natureza"
    if any(
        w in t
        for w in [
            "água",
            "balnear",
            "praia",
            "torneira",
            "nitratos",
            "residuai",
            "esgoto",
            "eutrofiz",
        ]
    ):
        return "Água e Qualidade Ambiental"
    if any(
        w in t
        for w in [
            "autoestrada",
            "auto-estrada",
            "auto estrada",
            "ren ",
            "reserva ecológica",
            "pooc",
            "ordenament",
            "urbaniz",
            "empreendiment",
            "construção",
            "pedreira",
            "designer village",
            "fanal",
            "silos",
            "ic 16",
            "ic3",
            "ic16",
        ]
    ):
        return "Ordenamento do Território"
    if any(
        w in t
        for w in [
            "conservação",
            "natureza",
            "biodiversidad",
            "mindelo",
            "barrinha",
            "sabor",
            "alqueva",
            "barrag",
            "rio tinto",
            "abutre",
            "zona húmida",
            "paúl",
            "tejo internacional",
            "estuário",
            "sapal",
            "lagoa",
            "reserva",
            "parque natural",
            "aves",
            "madeira tropical",
            "coral bulker",
            "salamanca",
            "rios internacionais",
            "gasoduto",
        ]
    ):
        return "Conservação da Natureza"
    if any(
        w in t
        for w in [
            "poluição",
            "poluent",
            "polui",
            "petrogal",
            "contamina",
            "lisnave",
            "navio",
            "ruído",
            "antena",
            "umts",
            "amianto",
            "urânio",
            "mina",
            "qualidade do ar",
            "cheia",
        ]
    ):
        return "Política Ambiental e Outros"
    return "Política Ambiental e Outros"


cats = defaultdict(list)
for item in comunicados:
    cat = categorize(item["title"], item.get("html", ""))
    cats[cat].append(item)

THEME_ORDER = [
    "Conservação da Natureza",
    "Água e Qualidade Ambiental",
    "Floresta",
    "Alimentação e OGM",
    "Resíduos e Reciclagem",
    "Energia e Clima",
    "Transportes e Mobilidade",
    "Ordenamento do Território",
    "Política Ambiental e Outros",
]

WANTED_PAGE_SECTIONS = {"Ecografia", "Barrinha de Esmoriz", "Rio Tinto"}

# --- Build sections ---
sections_html = ""
total_items = 0

for theme in THEME_ORDER:
    items = cats.get(theme, [])
    if not items:
        continue
    items.sort(key=lambda x: x.get("date", ""))

    section_id = (
        theme.lower()
        .replace(" ", "-")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    sections_html += f'    <section id="{section_id}">\n'
    sections_html += (
        f'      <h2>{theme} <span class="section-count">{len(items)}</span></h2>\n'
    )

    for item in items:
        title = html.escape(item["title"])
        date = item.get("date", "")
        content = item.get("html", "")
        total_items += 1

        sections_html += '      <details class="texto-item">\n'
        sections_html += '        <summary class="texto-header">\n'
        sections_html += f'          <span class="texto-date">{date}</span>\n'
        sections_html += f'          <span class="texto-title">{title}</span>\n'
        sections_html += "        </summary>\n"
        sections_html += (
            f'        <div class="texto-body">\n{content}\n        </div>\n'
        )
        sections_html += "      </details>\n"

    sections_html += "    </section>\n\n"

# --- Pages sections (Ecografia, Barrinha, Rio Tinto) ---
for sec_name in ["Ecografia", "Barrinha de Esmoriz", "Rio Tinto"]:
    sec_items = [p for p in paginas if p.get("section") == sec_name]
    sec_items = [p for p in sec_items if len(p.get("html", "")) > 200]
    if not sec_items:
        continue
    sec_items.sort(key=lambda x: x.get("title", ""))

    section_id = sec_name.lower().replace(" ", "-").replace("í", "i")
    sections_html += f'    <section id="{section_id}">\n'
    sections_html += f'      <h2>{sec_name} <span class="section-count">{len(sec_items)}</span></h2>\n'

    for item in sec_items:
        raw_title = item.get("title", "Sem título")
        title = html.escape(raw_title)
        title = re.sub(r"^(Áreas Naturais|Problemas ambientais)\s*»\s*", "", title)
        title = re.sub(
            r"^(Barrinha de Esmoriz|Rio Tinto entubado|Ecografia)\s*»?\s*", "", title
        )
        if not title:
            title = html.escape(raw_title)
        date = item.get("date", "")
        content = item.get("html", "")
        total_items += 1

        sections_html += '      <details class="texto-item">\n'
        sections_html += '        <summary class="texto-header">\n'
        if date:
            sections_html += f'          <span class="texto-date">{date}</span>\n'
        sections_html += f'          <span class="texto-title">{title}</span>\n'
        sections_html += "        </summary>\n"
        sections_html += (
            f'        <div class="texto-body">\n{content}\n        </div>\n'
        )
        sections_html += "      </details>\n"

    sections_html += "    </section>\n\n"

# --- TOC ---
toc_items = []
for theme in THEME_ORDER:
    if cats.get(theme):
        tid = (
            theme.lower()
            .replace(" ", "-")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )
        toc_items.append(f'        <a href="#{tid}">{theme}</a>')
for sec_name in ["Ecografia", "Barrinha de Esmoriz", "Rio Tinto"]:
    sec_items = [
        p
        for p in paginas
        if p.get("section") == sec_name and len(p.get("html", "")) > 200
    ]
    if sec_items:
        tid = sec_name.lower().replace(" ", "-").replace("í", "i")
        toc_items.append(f'        <a href="#{tid}">{sec_name}</a>')
toc_pills = "\n".join(toc_items)

# --- Full HTML ---
page_html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quercus — Núcleo do Porto — Nuno Quental</title>

  <meta name="description" content="Comunicados de imprensa e textos do Núcleo do Porto da Quercus (1998–2002), organizados por tema.">
  <link rel="canonical" href="https://coolio1.github.io/activismo-quercus.html">
  <link rel="icon" type="image/png" href="favicon.png">
  <link rel="icon" type="image/x-icon" href="favicon.ico">

  <link rel="stylesheet" href="style.css">
  <style>
    .texto-item {{ margin-bottom: 0.5rem; }}
    .texto-header {{
      display: flex; align-items: baseline; gap: 1rem;
      padding: 1rem 1.5rem; border-radius: 8px; border: 1px solid transparent;
      cursor: pointer; transition: all 0.3s ease; list-style: none;
      width: 100%; background: none; text-align: left;
      font-family: inherit; font-size: 0.92rem; color: var(--ink-light); line-height: 1.7;
    }}
    .texto-header:hover {{ background: var(--bg-warm); border-color: var(--border); }}
    .texto-header::before {{
      content: '\\25B8'; flex-shrink: 0; font-size: 0.75rem;
      color: var(--accent); transition: transform 0.3s ease;
    }}
    .texto-item[open] > .texto-header::before {{ transform: rotate(90deg); }}
    .texto-date {{
      flex-shrink: 0; font-size: 0.78rem; font-weight: 600;
      color: var(--ink-muted); letter-spacing: 0.02em; min-width: 6rem;
    }}
    .texto-title {{ color: var(--ink); font-weight: 500; }}
    .texto-body {{
      padding: 0.5rem 1.5rem 1.5rem 3.5rem; font-size: 0.9rem;
      color: var(--ink-light); line-height: 1.85; max-width: 760px;
    }}
    .texto-body p {{ margin-bottom: 0.8rem; }}
    .texto-body p:last-child {{ margin-bottom: 0; }}
    .texto-body table {{ border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem; }}
    .texto-body td, .texto-body th {{ border: 1px solid var(--border); padding: 0.4rem 0.6rem; }}
    .texto-body th {{ background: var(--bg-warm); font-weight: 600; }}
    .texto-body ul, .texto-body ol {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
    .texto-body li {{ margin-bottom: 0.3rem; }}
    .texto-body h1, .texto-body h2, .texto-body h3, .texto-body h4 {{
      font-family: 'Playfair Display', Georgia, serif;
      color: var(--ink); margin: 1.2rem 0 0.5rem;
    }}
    .texto-body h1 {{ font-size: 1.2rem; }}
    .texto-body h2 {{ font-size: 1.1rem; }}
    .texto-body h3 {{ font-size: 1rem; text-transform: none; letter-spacing: 0; }}
    .back-link {{
      display: inline-block; margin-bottom: 1rem; color: var(--accent);
      text-decoration: none; font-size: 0.85rem; font-weight: 500;
    }}
    .back-link:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <nav>
      <a href="index.html" class="nav-name">NQ</a>
      <div class="nav-links">
        <a href="index.html">Início</a>
        <a href="escritos.html">Publicações</a>
        <a href="activismo.html" class="active">Activismo</a>
        <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/" target="_blank">Porto Verde</a>
      </div>
    </nav>
  </header>

  <main>
    <a href="activismo.html" class="back-link">&larr; Activismo Cívico</a>
    <div class="page-header">
      <h1>Quercus — Núcleo do Porto</h1>
      <p class="intro">Coordenação do Núcleo do Porto da Quercus — Associação Nacional de Conservação da Natureza (1998–2002). {total_items} textos organizados por tema, incluindo comunicados de imprensa, pareceres e boletins.</p>
    </div>

    <nav class="toc">
      <strong>{total_items} textos</strong>
      <div class="toc-links">
{toc_pills}
      </div>
    </nav>

{sections_html}  </main>

  <footer>
    <p><a href="https://www.linkedin.com/in/nquental" target="_blank">Nuno Quental</a> &copy; 2026</p>
  </footer>
</body>
</html>
"""

output_path = os.path.join(SITE, "activismo-quercus.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(page_html)

print(f"Generated activismo-quercus.html ({total_items} items)")
for theme in THEME_ORDER:
    if cats.get(theme):
        print(f"  {theme}: {len(cats[theme])}")
for sec_name in ["Ecografia", "Barrinha de Esmoriz", "Rio Tinto"]:
    sec_items = [
        p
        for p in paginas
        if p.get("section") == sec_name and len(p.get("html", "")) > 200
    ]
    if sec_items:
        print(f"  {sec_name}: {len(sec_items)}")
