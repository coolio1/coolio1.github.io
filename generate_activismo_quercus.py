"""Generate activismo-quercus.html from extracted JSON data."""
import json, sys, html, re, os

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)

SITE = r'C:\Users\quent\Downloads\Claude\CV'

with open(os.path.join(SITE, 'data', 'quercus_comunicados.json'), 'r', encoding='utf-8') as f:
    comunicados = json.load(f)

with open(os.path.join(SITE, 'data', 'quercus_paginas.json'), 'r', encoding='utf-8') as f:
    paginas = json.load(f)

# --- Categorization ---
def categorize(title, text):
    t = (title + ' ' + text[:500]).lower()
    if any(w in t for w in ['co-inciner', 'resíduo', 'reciclagem', 'aterro', 'embalage', 'pilha',
                             'óleos usados', 'pneus usados', 'lixo', 'hospitalar']):
        return 'Resíduos e Reciclagem'
    if any(w in t for w in ['transgénico', 'geneticamente modificado', 'ogm', 'dioxina',
                             'alimento contaminad', 'biosegurança', 'bio(in)segurança']):
        return 'Alimentação e OGM'
    if any(w in t for w in ['alteraç', 'climátic', 'quioto', 'kyoto', 'marraque', 'haia',
                             'emissõ', 'ozono', 'co2', 'carbono', 'energia']):
        return 'Energia e Clima'
    if any(w in t for w in ['transport', 'aeroporto', 'ponte 25', 'comboio', 'combóio', 'portag',
                             'carris', 'eléctric', 'sem carro', 'veículo', 'automóv', 'aviação',
                             'mtbe', 'gasolina', 'gasóleo']):
        return 'Transportes e Mobilidade'
    if any(w in t for w in ['floresta', 'eucalipt', 'sobreir', 'montado', 'cortiça', 'fogo',
                             'incêndio', 'arrase de vegetação']):
        return 'Floresta'
    if any(w in t for w in ['caça', 'caca', 'venatór', 'não caça']):
        return 'Conservação da Natureza'
    if any(w in t for w in ['água', 'balnear', 'praia', 'torneira', 'nitratos', 'residuai',
                             'esgoto', 'eutrofiz']):
        return 'Água e Qualidade Ambiental'
    if any(w in t for w in ['autoestrada', 'auto-estrada', 'auto estrada', 'ren ', 'reserva ecológica',
                             'pooc', 'ordenament', 'urbaniz', 'empreendiment', 'construção', 'pedreira',
                             'designer village', 'fanal', 'silos', 'ic 16', 'ic3', 'ic16']):
        return 'Ordenamento do Território'
    if any(w in t for w in ['conservação', 'natureza', 'biodiversidad', 'mindelo', 'barrinha', 'sabor',
                             'alqueva', 'barrag', 'rio tinto', 'abutre', 'zona húmida', 'paúl',
                             'tejo internacional', 'estuário', 'sapal', 'lagoa', 'reserva',
                             'parque natural', 'aves', 'madeira tropical', 'coral bulker',
                             'salamanca', 'rios internacionais', 'gasoduto']):
        return 'Conservação da Natureza'
    if any(w in t for w in ['poluição', 'poluent', 'polui', 'petrogal', 'contamina', 'lisnave',
                             'navio', 'ruído', 'antena', 'umts', 'amianto', 'urânio', 'mina',
                             'qualidade do ar', 'cheia']):
        return 'Política Ambiental e Outros'
    if any(w in t for w in ['balanço', 'desafio', 'proposta', 'recomendaç', 'orçamento', 'cimeira',
                             'presidência', 'indicador', 'eleições', 'autárquic', 'encontro',
                             'governo', 'prémio', 'natal', '15 anos']):
        return 'Política Ambiental e Outros'
    return 'Política Ambiental e Outros'

# Categorize and group
from collections import defaultdict
cats = defaultdict(list)
for item in comunicados:
    cat = categorize(item['title'], item['text'])
    cats[cat].append(item)

# Theme order
THEME_ORDER = [
    'Conservação da Natureza',
    'Água e Qualidade Ambiental',
    'Floresta',
    'Alimentação e OGM',
    'Resíduos e Reciclagem',
    'Energia e Clima',
    'Transportes e Mobilidade',
    'Ordenamento do Território',
    'Política Ambiental e Outros',
]

# Also add selected pages
WANTED_PAGE_SECTIONS = {'Ecografia', 'Barrinha de Esmoriz', 'Rio Tinto'}

# --- Text to HTML paragraphs ---
def text_to_html(text):
    """Convert plain text to HTML paragraphs."""
    text = html.escape(text)
    # Split on double newlines for paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    # Filter empty and very short (just whitespace)
    paragraphs = [p.strip().replace('\n', '<br>') for p in paragraphs if p.strip()]
    return '\n'.join(f'          <p>{p}</p>' for p in paragraphs)

# --- Large items threshold ---
LARGE_THRESHOLD = 15000
PDF_DIR = 'pdfs/Voluntariado/Quercus'

def get_pdf_href(item):
    """Find matching PDF for a large item."""
    title = item['title']
    date = item.get('date', '')
    safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:80].strip()
    pdf_name = f'{date} - {safe_title}.pdf'
    pdf_path = os.path.join(SITE, PDF_DIR, pdf_name)
    if os.path.exists(pdf_path):
        return f'{PDF_DIR}/{pdf_name}'
    return None

# --- Build sections ---
sections_html = ''
total_embedded = 0
total_items = 0

for theme in THEME_ORDER:
    items = cats.get(theme, [])
    if not items:
        continue
    items.sort(key=lambda x: x.get('date', ''))

    section_id = theme.lower().replace(' ', '-').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    sections_html += f'    <section id="{section_id}">\n'
    sections_html += f'      <h2>{theme} <span class="section-count">{len(items)}</span></h2>\n'

    for item in items:
        title = html.escape(item['title'])
        date = item.get('date', '')
        text = item['text']
        nchars = len(text)
        total_items += 1

        pdf_href = get_pdf_href(item) if nchars > LARGE_THRESHOLD else None
        pdf_badge = f' <a href="{pdf_href}" class="pdf-link" title="Descarregar PDF" target="_blank">PDF</a>' if pdf_href else ''

        sections_html += f'      <details class="texto-item">\n'
        sections_html += f'        <summary class="texto-header">\n'
        sections_html += f'          <span class="texto-date">{date}</span>\n'
        sections_html += f'          <span class="texto-title">{title}{pdf_badge}</span>\n'
        sections_html += f'        </summary>\n'
        sections_html += f'        <div class="texto-body">\n'
        sections_html += text_to_html(text)
        sections_html += f'\n        </div>\n'
        sections_html += f'      </details>\n'
        total_embedded += 1

    sections_html += f'    </section>\n\n'

# --- Pages sections (Ecografia, Barrinha, Rio Tinto) ---
for sec_name in ['Ecografia', 'Barrinha de Esmoriz', 'Rio Tinto']:
    sec_items = [p for p in paginas if p.get('section') == sec_name]
    # Skip index/navigation pages (very short)
    sec_items = [p for p in sec_items if len(p.get('text', '')) > 400]
    if not sec_items:
        continue
    sec_items.sort(key=lambda x: x.get('title', ''))

    section_id = sec_name.lower().replace(' ', '-').replace('í', 'i')
    sections_html += f'    <section id="{section_id}">\n'
    sections_html += f'      <h2>{sec_name} <span class="section-count">{len(sec_items)}</span></h2>\n'

    for item in sec_items:
        raw_title = item.get('title', 'Sem título')
        title = html.escape(raw_title)
        # Clean up long prefixed titles
        title = re.sub(r'^(Áreas Naturais|Problemas ambientais)\s*»\s*', '', title)
        title = re.sub(r'^(Barrinha de Esmoriz|Rio Tinto entubado|Ecografia)\s*»?\s*', '', title)
        if not title:
            title = html.escape(raw_title)
        date = item.get('date', '')
        text = item['text']
        nchars = len(text)
        total_items += 1
        total_embedded += 1

        # Check for PDF (large Barrinha pages)
        pdf_badge = ''
        if nchars > LARGE_THRESHOLD:
            safe_t = re.sub(r'[<>:"/\\|?*]', '', raw_title)[:60].strip()
            pdf_name = f'Barrinha de Esmoriz - {safe_t}.pdf'
            pdf_path = os.path.join(SITE, PDF_DIR, pdf_name)
            if os.path.exists(pdf_path):
                pdf_badge = f' <a href="{PDF_DIR}/{pdf_name}" class="pdf-link" title="Descarregar PDF" target="_blank">PDF</a>'

        sections_html += f'      <details class="texto-item">\n'
        sections_html += f'        <summary class="texto-header">\n'
        if date:
            sections_html += f'          <span class="texto-date">{date}</span>\n'
        sections_html += f'          <span class="texto-title">{title}{pdf_badge}</span>\n'
        sections_html += f'        </summary>\n'
        sections_html += f'        <div class="texto-body">\n'
        sections_html += text_to_html(text)
        sections_html += f'\n        </div>\n'
        sections_html += f'      </details>\n'

    sections_html += f'    </section>\n\n'

# --- TOC pills ---
toc_items = []
for theme in THEME_ORDER:
    if cats.get(theme):
        tid = theme.lower().replace(' ', '-').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        toc_items.append(f'        <a href="#{tid}">{theme}</a>')
for sec_name in ['Ecografia', 'Barrinha de Esmoriz', 'Rio Tinto']:
    sec_items = [p for p in paginas if p.get('section') == sec_name and len(p.get('text', '')) > 400]
    if sec_items:
        tid = sec_name.lower().replace(' ', '-').replace('í', 'i')
        toc_items.append(f'        <a href="#{tid}">{sec_name}</a>')
toc_pills = '\n'.join(toc_items)

# --- Full HTML ---
page_html = f'''<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quercus — Núcleo do Porto — Nuno Quental</title>

  <meta name="description" content="198 comunicados de imprensa e textos do Núcleo do Porto da Quercus (1998–2002), organizados por tema.">
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
      color: var(--ink-light); line-height: 1.85; max-width: 720px;
    }}
    .texto-body p {{ margin-bottom: 0.8rem; }}
    .texto-body p:last-child {{ margin-bottom: 0; }}
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
'''

output_path = os.path.join(SITE, 'activismo-quercus.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(page_html)

print(f'Generated activismo-quercus.html ({total_items} items, {total_embedded} embedded)')
for theme in THEME_ORDER:
    if cats.get(theme):
        print(f'  {theme}: {len(cats[theme])}')
for sec_name in ['Ecografia', 'Barrinha de Esmoriz', 'Rio Tinto']:
    sec_items = [p for p in paginas if p.get('section') == sec_name and len(p.get('text', '')) > 400]
    if sec_items:
        print(f'  {sec_name}: {len(sec_items)}')
