"""Generate activismo-parque.html from MPC comunicados HTML data."""

import json
import sys
import html
import os

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)

SITE = r"C:\Users\quent\Downloads\Claude\CV"

with open(
    os.path.join(SITE, "data", "mpc_comunicados_html.json"), "r", encoding="utf-8"
) as f:
    comunicados = json.load(f)

comunicados.sort(key=lambda x: x.get("date", ""))
total = len(comunicados)

# Build items
items_html = ""
for item in comunicados:
    title = html.escape(item["title"])
    date = item.get("date", "")
    content = item.get("html", "")

    items_html += '      <details class="texto-item">\n'
    items_html += '        <summary class="texto-header">\n'
    items_html += f'          <span class="texto-date">{date}</span>\n'
    items_html += f'          <span class="texto-title">{title}</span>\n'
    items_html += "        </summary>\n"
    items_html += f'        <div class="texto-body">\n{content}\n        </div>\n'
    items_html += "      </details>\n"

page_html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Movimento pelo Parque da Cidade — Nuno Quental</title>

  <meta name="description" content="22 comunicados do Movimento pelo Parque da Cidade do Porto (2001–2003) — do manifesto fundador à vitória.">
  <link rel="canonical" href="https://coolio1.github.io/activismo-parque.html">
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
      <h1>Movimento pelo Parque da Cidade</h1>
      <p class="intro">Movimento cívico pela defesa do Parque da Cidade do Porto contra a urbanização (2001–2003). Do manifesto fundador à vitória — {total} comunicados.</p>
    </div>

    <section id="comunicados">
      <h2>Comunicados <span class="section-count">{total}</span></h2>
{items_html}
    </section>

  </main>

  <footer>
    <p><a href="https://www.linkedin.com/in/nquental" target="_blank">Nuno Quental</a> &copy; 2026</p>
  </footer>
</body>
</html>
"""

output_path = os.path.join(SITE, "activismo-parque.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(page_html)

print(f"Generated activismo-parque.html ({total} comunicados)")
