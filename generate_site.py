"""Generate the full academic portfolio site from Zotero export data."""
import sys, io, os, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EXPORT = r'C:\Users\quent\Zotero\export.json'
SITE = r'C:\Users\quent\Downloads\Claude\CV'
PDFS_DIR = os.path.join(SITE, 'pdfs')

with open(EXPORT, 'r', encoding='utf-8') as f:
    items = json.load(f)

# Fix missing dates in Zotero export
DATE_OVERRIDES = {
    55: '2009',    # Naturbanization
    97: '2015',    # Changing the future of energy
    99: '2006',    # Plano Estratégico Ponte da Barca
    96: '2003',    # Portuguese environmental policy (conference)
}
for item in items:
    if item['itemID'] in DATE_OVERRIDES and not item.get('date'):
        item['date'] = DATE_OVERRIDES[item['itemID']]

# Exclude Carta policiario and Acknowledgement to Reviewers
EXCLUDE_IDS = set()
for item in items:
    t = (item.get('title') or '').lower()
    if 'carta' in t and 'polici' in t:
        EXCLUDE_IDS.add(item['itemID'])
    if 'acknowledgement to reviewers' in t.lower() or 'agradecimento aos reviewers' in t.lower():
        EXCLUDE_IDS.add(item['itemID'])
    if item['itemID'] == 229:  # Terraços - Livro Rio Fernandes
        EXCLUDE_IDS.add(item['itemID'])
    if item['itemID'] == 246:  # A envolvente da Casa da Música - duplicado de "A Casa em debate" (ID=167)
        EXCLUDE_IDS.add(item['itemID'])

items = [i for i in items if i['itemID'] not in EXCLUDE_IDS]

def extract_year(date_str):
    if not date_str:
        return ''
    m = re.search(r'(\d{4})', date_str)
    return m.group(1) if m else ''

def format_authors_apa(creators):
    """Format authors in APA 7 style."""
    authors = [c for c in creators if c['type'] == 'author']
    if not authors:
        return ''
    parts = []
    for a in authors:
        last = a['last']
        first = a['first']
        if not first:  # Institutional author
            parts.append(last)
        else:
            initials = ' '.join([n[0] + '.' for n in first.split() if n])
            parts.append(f'{last}, {initials}')
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f'{parts[0]} & {parts[1]}'
    else:
        return ', '.join(parts[:-1]) + ', & ' + parts[-1]

def format_apa(item):
    """Generate APA 7 citation."""
    authors = format_authors_apa(item.get('creators', []))
    year = extract_year(item.get('date'))
    title = item.get('title', '')
    typ = item.get('typeName', '')
    pub = item.get('publicationTitle') or ''
    book = item.get('bookTitle') or ''
    vol = item.get('volume') or ''
    iss = item.get('issue') or ''
    pages = item.get('pages') or ''
    doi = item.get('doi') or ''
    publisher = item.get('publisher') or ''
    place = item.get('place') or ''

    year_str = f'({year})' if year else '(s.d.)'

    institution = item.get('institution') or ''
    conf = item.get('conferenceName') or ''
    proc = item.get('proceedingsTitle') or ''
    isbn = item.get('ISBN') or ''
    issn = item.get('ISSN') or ''
    university = item.get('university') or ''
    thesis_type = item.get('thesisType') or ''

    if typ == 'journalArticle':
        title_end = '.' if not title.endswith(('?', '!')) else ''
        ref = f'{authors} {year_str}. {title}{title_end}'
        if pub:
            ref += f' <em>{pub}</em>'
            if vol:
                ref += f', <em>{vol}</em>'
            if iss:
                if vol:
                    ref += f'({iss})'
                else:
                    ref += f' ({iss})'
            if pages:
                ref += f', {pages}'
            ref += '.'
        if doi:
            doi_url = f'https://doi.org/{doi}'
            ref += f' <a href="{doi_url}" target="_blank">{doi_url}</a>'
    elif typ == 'bookSection':
        editors = [c for c in item.get('creators', []) if c['type'] == 'editor']
        ed_str = ''
        if editors:
            ed_parts = [f"{e['first'][0]}. {e['last']}" if e['first'] else e['last'] for e in editors]
            ed_str = ', '.join(ed_parts)
            ed_str = f' Em {ed_str} (Ed.),'
        # Avoid double period if title already ends with punctuation
        title_end = '.' if not title.endswith(('.', '?', '!')) else ''
        ref = f'{authors} {year_str}. {title}{title_end}{ed_str}'
        if book:
            ref += f' <em>{book}</em>'
        if pages:
            ref += f' (pp. {pages})'
        ref += '.'
        if publisher:
            ref += f' {publisher}'
        if place:
            ref += f', {place}'
        if (publisher or place) and not ref.endswith('.'):
            ref += '.'
    elif typ == 'thesis':
        ref = f'{authors} {year_str}. <em>{title}</em>'
        if thesis_type:
            ref += f' [{thesis_type}]'
        ref += '.'
        if university:
            ref += f' {university}'
        if place:
            ref += f', {place}'
        if (university or place) and not ref.endswith('.'):
            ref += '.'
    elif typ == 'report':
        editors = [c for c in item.get('creators', []) if c['type'] == 'editor']
        ref = f'{authors} {year_str}. <em>{title}</em>.'
        if editors:
            ed_parts = [f"{e['first'][0]}. {e['last']}" if e['first'] else e['last'] for e in editors]
            ed_str = ', '.join(ed_parts)
            ref += f' Coordenação de {ed_str}.'
        if institution:
            ref += f' {institution}'
        elif publisher:
            ref += f' {publisher}'
        if place:
            ref += f', {place}'
        if (institution or publisher or place) and not ref.endswith('.'):
            ref += '.'
    elif typ in ('newspaperArticle', 'magazineArticle'):
        title_end = '.' if not title.endswith(('?', '!')) else ''
        ref = f'{authors} {year_str}. {title}{title_end}'
        if pub:
            ref += f' <em>{pub}</em>'
            if vol:
                ref += f', <em>{vol}</em>'
            if iss:
                if vol:
                    ref += f'({iss})'
                else:
                    ref += f' ({iss})'
            if pages:
                ref += f', {pages}'
            ref += '.'
        else:
            pass  # no pub
    elif typ == 'conferencePaper':
        title_end = '.' if not title.endswith(('?', '!')) else ''
        ref = f'{authors} {year_str}. {title}{title_end}'
        if proc:
            ref += f' Em <em>{proc}</em>'
            if pages:
                ref += f' (pp. {pages})'
            ref += '.'
        elif conf:
            ref += f' <em>{conf}</em>'
            if place:
                ref += f', {place}'
            if pages:
                ref += f' (pp. {pages})'
            ref += '.'
        if publisher and not proc:
            ref += f' {publisher}'
            if not ref.endswith('.'):
                ref += '.'
        if isbn:
            ref += f' ISBN {isbn}.'
    else:
        title_end = '.' if not title.endswith(('?', '!')) else ''
        ref = f'{authors} {year_str}. {title}{title_end}'

    return ref

COVERS_DIR = os.path.join(SITE, 'covers')

def get_cover_filename(item):
    """Find cover image for this item."""
    import unicodedata
    for att in item.get('attachments', []):
        basename = os.path.basename(att)
        jpg_name = os.path.splitext(basename)[0] + '.jpg'
        if os.path.exists(os.path.join(COVERS_DIR, jpg_name)):
            return jpg_name
        ascii_name = unicodedata.normalize('NFD', jpg_name).encode('ascii', 'ignore').decode()
        if os.path.exists(os.path.join(COVERS_DIR, ascii_name)):
            return ascii_name
    return None

def get_pdf_filename(item):
    """Find the PDF filename for this item in pdfs/ dir."""
    import unicodedata
    for att in item.get('attachments', []):
        basename = os.path.basename(att)
        pdf_name = os.path.splitext(basename)[0] + '.pdf'
        # Try exact match
        if os.path.exists(os.path.join(PDFS_DIR, pdf_name)):
            return pdf_name
        if os.path.exists(os.path.join(PDFS_DIR, basename)):
            return basename
        # Try ASCII-normalized version (e.g. Terraços -> Terracos)
        ascii_name = unicodedata.normalize('NFD', pdf_name).encode('ascii', 'ignore').decode()
        if os.path.exists(os.path.join(PDFS_DIR, ascii_name)):
            return ascii_name
    return None

def categorize(item):
    typ = item.get('typeName', '')
    title = (item.get('title') or '').lower()
    pub = (item.get('publicationTitle') or '').lower()

    # Use attachment paths to help categorize
    atts = ' '.join(item.get('attachments', []))

    # Trabalhos universitários
    UNIVERSITY_IDS = {49, 76, 165, 255, 256, 257}
    if item.get('itemID') in UNIVERSITY_IDS:
        return 'universitario'
    if typ == 'thesis':
        if item.get('itemID') == 81:  # Spectral study = tese licenciatura
            return 'tese_lic'
        return 'tese'
    elif typ in ('journalArticle', 'bookSection', 'conferencePaper'):
        return 'cientifico'
    elif typ == 'report' or typ == 'magazineArticle':
        return 'trabalhos'
    elif typ == 'newspaperArticle':
        iid = item.get('itemID')
        # Policiário
        if 'polici' in title or 'inspector' in title or '4 faces' in title:
            return 'policiario'
        # COVID
        if 'COVID' in atts or 'covid' in title:
            return 'op_covid'
        # Mobilidade e Transportes
        MOBILITY_IDS = {178, 172, 164, 202, 204}
        if iid in MOBILITY_IDS:
            return 'op_mobilidade'
        # Cidade, Urbanismo e Espaços Verdes
        CITY_IDS = {182, 177, 168, 167, 166, 185, 162, 161, 190, 188, 184,
                    163, 174, 205, 201, 173, 181, 246, 248}
        if iid in CITY_IDS:
            return 'op_cidade'
        # Ambiente e Sustentabilidade (tudo o resto)
        return 'op_ambiente'
    else:
        return 'outros'

# Categorize all items
categories = {
    'tese': [],
    'tese_lic': [],
    'cientifico': [],
    'universitario': [],
    'trabalhos': [],
    'op_cidade': [],
    'op_ambiente': [],
    'op_mobilidade': [],
    'op_covid': [],
    'policiario': [],
}

for item in items:
    cat = categorize(item)
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(item)

# Sort each category by year descending
for cat in categories:
    categories[cat].sort(key=lambda x: extract_year(x.get('date', '')) or '0000', reverse=True)

# Count totals
total = sum(len(v) for v in categories.values())
print(f'Total items for site: {total}')
for cat, items_list in categories.items():
    print(f'  {cat}: {len(items_list)}')

# --- Generate escritos.html ---

# Consolidated structure: 5 top-level sections, opinion has subsections
top_sections = [
    {
        'id': 'teses',
        'label': 'Teses',
        'subs': [
            ('Doutoramento', categories.get('tese', [])),
            ('Licenciatura', categories.get('tese_lic', [])),
        ]
    },
    {
        'id': 'cientifico',
        'label': 'Artigos Científicos',
        'subs': [('', categories.get('cientifico', []))],
    },
    {
        'id': 'trabalhos',
        'label': 'Relatórios Técnicos',
        'nav_label': 'Relatórios',
        'subs': [('', categories.get('trabalhos', []))],
    },
    {
        'id': 'opiniao',
        'label': 'Artigos de Opinião',
        'subs': [
            ('Cidade, Urbanismo e Espaços Verdes', categories.get('op_cidade', [])),
            ('Ambiente e Sustentabilidade', categories.get('op_ambiente', [])),
            ('Mobilidade e Transportes', categories.get('op_mobilidade', [])),
            ('COVID-19', categories.get('op_covid', [])),
        ]
    },
    {
        'id': 'policiario',
        'label': 'Ficção Policial',
        'subs': [('', categories.get('policiario', []))],
    },
    {
        'id': 'universitario',
        'label': 'Trabalhos Universitários',
        'nav_label': 'Universidade',
        'subs': [('', categories.get('universitario', []))],
    },
]

def render_items(items_list, show_covers=False, show_year_markers=False):
    html = ''
    last_year = None
    for item in items_list:
        year = extract_year(item.get('date', ''))
        # Year separator
        if show_year_markers and year and year != last_year:
            html += f'        <li class="year-marker" aria-hidden="true"><span>{year}</span></li>\n'
            last_year = year
        apa = format_apa(item)
        pdf = get_pdf_filename(item)
        cover = get_cover_filename(item) if show_covers else None
        doi = item.get('doi')
        url = item.get('url')
        pdf_badge = f' <a href="pdfs/{pdf}" class="pdf-link" title="Descarregar PDF" target="_blank">PDF</a>' if pdf else ''
        url_badge = f' <a href="{url}" class="url-link" title="Ver online" target="_blank">URL</a>' if url else ''
        badges = pdf_badge + url_badge
        if cover and pdf:
            html += f'        <li class="has-cover"><a href="pdfs/{pdf}" target="_blank" class="cover-thumb"><img src="covers/{cover}" alt="" loading="lazy"></a><div>{apa}{badges}</div></li>\n'
        else:
            html += f'        <li>{apa}{badges}</li>\n'
    return html

# Featured items (destaques)
FEATURED_IDS = [79, 59, 57, 58, 55, 100]  # Tese, Scientometrics, Env Dev Sust, Sust Dev, Naturbanization, SET Plan
featured_items = [item for item in items if item['itemID'] in FEATURED_IDS]
featured_items.sort(key=lambda x: FEATURED_IDS.index(x['itemID']))

def render_featured(items_list):
    html = ''
    for item in items_list:
        title = item.get('title', '')
        year = extract_year(item.get('date', ''))
        pdf = get_pdf_filename(item)
        cover = get_cover_filename(item)
        authors = format_authors_apa(item.get('creators', []))
        pub = item.get('publicationTitle') or item.get('publisher') or ''
        link = f'pdfs/{pdf}' if pdf else '#'
        cover_html = f'<img src="covers/{cover}" alt="" loading="lazy">' if cover else '<div class="no-cover"></div>'
        html += f'''      <a href="{link}" target="_blank" class="featured-card">
        <div class="featured-cover">{cover_html}</div>
        <div class="featured-info">
          <span class="featured-year">{year}</span>
          <h3>{title}</h3>
          <p>{authors}</p>
          <p class="featured-pub">{pub}</p>
        </div>
      </a>\n'''
    return html

# Sections with covers: trabalhos, teses, cientifico
SECTIONS_WITH_COVERS = {'teses', 'universitario', 'trabalhos', 'cientifico'}
# Sections with year markers: opiniao (many items)
SECTIONS_WITH_YEARS = {'opiniao'}

escritos_sections = ''
for sec in top_sections:
    total_in_sec = sum(len(s[1]) for s in sec['subs'])
    if total_in_sec == 0:
        continue
    show_covers = sec['id'] in SECTIONS_WITH_COVERS
    show_years = sec['id'] in SECTIONS_WITH_YEARS
    escritos_sections += f'    <section id="{sec["id"]}">\n'
    escritos_sections += f'      <h2>{sec["label"]}</h2>\n'
    for sub_label, sub_items in sec['subs']:
        if not sub_items:
            continue
        if sub_label:
            escritos_sections += f'      <h3>{sub_label}</h3>\n'
        escritos_sections += f'      <ol class="publications">\n'
        escritos_sections += render_items(sub_items, show_covers=show_covers, show_year_markers=show_years)
        escritos_sections += f'      </ol>\n'
    escritos_sections += f'    </section>\n\n'

# Escolares section (Porto Editora PDFs — not from Zotero)
ESCOLARES_DIR = os.path.join(PDFS_DIR, 'Porto Editora')
ESCOLARES_EXCLUDE = {'as-dunas.pdf'}  # superseded by as-dunas-v2.pdf

ESCOLARES_TITLES = {
    'a-vida.pdf': 'A vida',
    'agricultura-e-diversidade.pdf': 'Agricultura e diversidade',
    'agricultura-e-domesticacao.pdf': 'Agricultura e domesticação',
    'animais-vs-plantas.pdf': 'Animais vs. plantas',
    'as-dunas-v2.pdf': 'As dunas',
    'aves-nas-cidades.pdf': 'Aves nas cidades',
    'biomas-e-factores-abioticos.pdf': 'Biomas e factores abióticos',
    'biotecnologia.pdf': 'Biotecnologia',
    'clima-e-ecossistemas.pdf': 'Clima e ecossistemas',
    'clima-esta-a-mudar.pdf': 'O clima está a mudar',
    'construir-ninhos.pdf': 'Construir ninhos',
    'descobrindo-o-litoral.pdf': 'Descobrindo o litoral',
    'diversidade-da-vida.pdf': 'Diversidade da vida',
    'ecossistemas.pdf': 'Ecossistemas',
    'escola-ecologica.pdf': 'Escola ecológica',
    'estrutura-das-plantas.pdf': 'Estrutura das plantas',
    'fazer-um-charco.pdf': 'Fazer um charco',
    'floresta-na-escola.pdf': 'Floresta na escola',
    'fontes-energeticas.pdf': 'Fontes energéticas',
    'golfinhos-do-sado.pdf': 'Golfinhos do Sado',
    'homem-e-biodiversidade.pdf': 'Homem e biodiversidade',
    'inspeccoes-costeiras.pdf': 'Inspecções costeiras',
    'o-lobo.pdf': 'O lobo',
    'poluicao-do-ar.pdf': 'Poluição do ar',
    'predacao-e-mimetismo.pdf': 'Predação e mimetismo',
    'residuos-e-reciclagem.pdf': 'Resíduos e reciclagem',
    'sabias-que-natureza.pdf': 'Sabias que… (natureza)',
    'sabias-que-reciclagem.pdf': 'Sabias que… (reciclagem)',
    'salvar-os-oceanos.pdf': 'Salvar os oceanos',
    'solo-e-rochas.pdf': 'Solo e rochas',
    'vida-em-perigo.pdf': 'Vida em perigo',
    'vida-nas-cidades-cont.pdf': 'Vida nas cidades (cont.)',
    'vida-nas-cidades.pdf': 'Vida nas cidades',
}

escolares_files = sorted(
    [f for f in os.listdir(ESCOLARES_DIR) if f.endswith('.pdf') and f not in ESCOLARES_EXCLUDE],
    key=lambda f: ESCOLARES_TITLES.get(f, f).lower()
)
escolares_section = '    <section id="escolares">\n'
escolares_section += '      <h2>Textos Escolares</h2>\n'
escolares_section += '      <ol class="publications">\n'
for f in escolares_files:
    title = ESCOLARES_TITLES.get(f, f.replace('-', ' ').replace('.pdf', '').title())
    href = f'pdfs/Porto Editora/{f}'
    escolares_section += f'        <li>{title} <a href="{href}" class="pdf-link" title="Descarregar PDF" target="_blank">PDF</a></li>\n'
escolares_section += '      </ol>\n'
escolares_section += '    </section>\n\n'
escritos_sections += escolares_section

toc_pills = '\n'.join([f'        <a href="#{sec["id"]}">{sec.get("nav_label", sec["label"])}</a>' for sec in top_sections if sum(len(s[1]) for s in sec['subs']) > 0])
toc_pills += '\n        <a href="#escolares">Escolares</a>'
total_items = sum(sum(len(s[1]) for s in sec['subs']) for sec in top_sections) + len(escolares_files)

escritos_html = f'''<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Publicações — Nuno Quental</title>

  <!-- SEO meta -->
  <meta name="description" content="Colecção de {total_items} publicações de Nuno Quental — artigos científicos, textos de opinião, trabalhos técnicos e profissionais sobre sustentabilidade, ambiente e urbanismo.">
  <link rel="canonical" href="https://coolio1.github.io/escritos.html">
  <link rel="icon" type="image/png" href="favicon.png">
  <link rel="icon" type="image/x-icon" href="favicon.ico">

  <!-- Open Graph -->
  <meta property="og:title" content="Publicações — Nuno Quental">
  <meta property="og:description" content="Colecção de {total_items} publicações sobre sustentabilidade, ambiente e urbanismo — da investigação académica à opinião pública.">
  <meta property="og:image" content="https://coolio1.github.io/nuno.jpg">
  <meta property="og:url" content="https://coolio1.github.io/escritos.html">
  <meta property="og:type" content="website">

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Publicações — Nuno Quental",
    "description": "Colecção de {total_items} publicações de Nuno Quental sobre sustentabilidade, ambiente e urbanismo.",
    "url": "https://coolio1.github.io/escritos.html",
    "author": {{
      "@type": "Person",
      "name": "Nuno Quental",
      "url": "https://coolio1.github.io/"
    }},
    "numberOfItems": {total_items}
  }}
  </script>

  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <nav>
      <a href="index.html" class="nav-name">NQ</a>
      <div class="nav-links">
        <a href="index.html">Início</a>
        <a href="escritos.html" class="active">Publicações</a>
        <a href="activismo.html">Activismo</a>
        <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/" target="_blank">Porto Verde</a>
      </div>
    </nav>
  </header>

  <main>
    <div class="page-header">
      <h1>Publicações</h1>
      <p class="intro">Compilação de {total_items} textos ao longo de mais de duas décadas — da investigação académica à opinião pública, passando por trabalhos técnicos e profissionais.</p>
    </div>

    <section id="destaques" class="featured-section">
      <h2>Destaques</h2>
      <div class="featured-grid">
{render_featured(featured_items)}      </div>
    </section>

    <nav class="toc">
      <strong>{total_items} publicações</strong>
      <div class="toc-links">
{toc_pills}
      </div>
    </nav>

{escritos_sections}  </main>

  <footer>
    <p><a href="https://www.linkedin.com/in/nquental" target="_blank">Nuno Quental</a> &copy; 2026</p>
  </footer>
</body>
</html>
'''

with open(os.path.join(SITE, 'escritos.html'), 'w', encoding='utf-8') as f:
    f.write(escritos_html)
print('Generated escritos.html')

# --- Generate index.html ---
index_html = f'''<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nuno Quental</title>

  <!-- SEO meta -->
  <meta name="description" content="Nuno Quental — engenheiro do ambiente e investigador em sustentabilidade urbana. Publicações académicas, projecto Porto Verde e percurso profissional na Comissão Europeia.">
  <meta name="keywords" content="Nuno Quental, engenheiro do ambiente, sustentabilidade urbana, Porto Verde, espaços verdes, Comissão Europeia, publicações, investigação, ambiente, Porto">
  <meta name="google-site-verification" content="Lkfn0DpuOYZdEePSv1vr4_iStVt6XfX5_mb4Sw3jXfY">
  <link rel="canonical" href="https://coolio1.github.io/">
  <link rel="icon" type="image/png" href="favicon.png">
  <link rel="icon" type="image/x-icon" href="favicon.ico">

  <!-- Open Graph -->
  <meta property="og:title" content="Nuno Quental — Engenheiro do Ambiente e Investigador">
  <meta property="og:description" content="Engenheiro do ambiente e investigador em sustentabilidade urbana. Publicações académicas, projecto Porto Verde e percurso profissional.">
  <meta property="og:image" content="https://coolio1.github.io/nuno.jpg">
  <meta property="og:url" content="https://coolio1.github.io/">
  <meta property="og:type" content="website">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Nuno Quental — Engenheiro do Ambiente e Investigador">
  <meta name="twitter:description" content="Engenheiro do ambiente e investigador em sustentabilidade urbana. Publicações académicas, projecto Porto Verde e percurso profissional.">
  <meta name="twitter:image" content="https://coolio1.github.io/nuno.jpg">

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Nuno Quental",
    "jobTitle": "Engenheiro do Ambiente",
    "description": "Investigador em sustentabilidade urbana e engenheiro do ambiente.",
    "url": "https://coolio1.github.io/",
    "image": "https://coolio1.github.io/nuno.jpg",
    "affiliation": {{
      "@type": "Organization",
      "name": "Comissão Europeia"
    }},
    "sameAs": [
      "https://www.linkedin.com/in/nquental",
      "https://scholar.google.com/citations?user=NoCUypYAAAAJ"
    ]
  }}
  </script>

  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <nav>
      <a href="index.html" class="nav-name">NQ</a>
      <div class="nav-links">
        <a href="index.html">Início</a>
        <a href="escritos.html">Publicações</a>
        <a href="activismo.html">Activismo</a>
        <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/" target="_blank">Porto Verde</a>
      </div>
    </nav>
  </header>

  <main>
    <section class="hero">
      <div class="hero-text">
        <h1>Nuno Quental</h1>
        <blockquote class="hero-quote">&laquo;Uma gestão urbanística correcta faz-se com a preservação, antes de mais, dos espaços verdes existentes.&raquo;</blockquote>
        <p class="hero-sub">Sustentabilidade urbana, energia e território.</p>
        <div class="hero-ctas">
          <a href="escritos.html" class="cta">Publicações &rarr;</a>
          <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/" target="_blank" class="cta cta-secondary">Mapeando o Verde do Porto &rarr;</a>
        </div>
      </div>
      <img src="nuno.jpg" alt="Nuno Quental" class="portrait">
    </section>

    <section class="projeto-destaque">
      <div class="projeto-texto">
        <span class="projeto-tag">Projecto em curso</span>
        <h2>Porto Verde</h2>
        <p>Mapas interactivos de vegetação, uso do solo e mudanças urbanas na cidade do Porto, com dados de satélite abertos. Como mudou a paisagem verde da cidade desde 1947?</p>
        <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/" target="_blank" class="cta cta-small">Explorar o projecto &rarr;</a>
        <h3 class="blog-heading">Últimos artigos</h3>
        <ul class="blog-list">
          <li>
            <time>30 Mar</time>
            <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/posts/acessibilidade-verde-publico-porto/" target="_blank">Acessibilidade a espaços verdes públicos no Porto</a>
          </li>
          <li>
            <time>21 Mar</time>
            <a href="https://coolio1.github.io/porto_areas_verdes_mudanca/posts/mudanca-verde-porto-1985-2025/" target="_blank">Dinâmicas de ocupação do solo e cobertura vegetal (1985–2025)</a>
          </li>
        </ul>
      </div>
      <div class="projeto-imagens">
        <figure>
          <img src="covers/porto_deficit.jpg" alt="Défice de espaços verdes no Porto" loading="lazy">
          <figcaption>Défice de espaços verdes</figcaption>
        </figure>
        <figure>
          <img src="covers/porto_2024.jpg" alt="Porto em 2024" loading="lazy">
          <figcaption>2024</figcaption>
        </figure>
      </div>
    </section>

    <section class="escritos-preview">
      <h2>Activismo Cívico</h2>
      <p style="color:var(--ink-light); font-size:0.95rem; line-height:1.8; margin-bottom:1.2rem;">Duas décadas de intervenção cívica e ambiental — do associativismo estudantil à coordenação do Núcleo do Porto da Quercus, passando pelo Movimento pelo Parque da Cidade e pela defesa do património urbano.</p>
      <ul class="blog-list">
        <li><time>1998–2002</time><a href="activismo-quercus.html">Quercus — Núcleo do Porto (213 textos)</a></li>
        <li><time>2001–2003</time><a href="activismo.html#parque-cidade">Movimento pelo Parque da Cidade</a></li>
        <li><time>~1995–2000</time><a href="activismo.html#farol-terra">Farol-Terra</a></li>
      </ul>
      <a href="activismo.html" class="ver-todos">Ver tudo &rarr;</a>
    </section>

    <aside class="pullquote">
      <blockquote>&laquo;A chave estará numa aposta múltipla: valorizar os planos, investir nas instituições, promover a cidadania activa e encarar os políticos como os primeiros guardiões e actores capazes de transformar as estratégias em realidade.&raquo;</blockquote>
      <cite>— Ordem nos planos, 2007</cite>
    </aside>

    <section class="bio">
      <h2>Sobre mim</h2>
      <p>Do Porto a Bruxelas, passando pela Alemanha e por um doutoramento no Instituto Superior Técnico — o meu percurso profissional tem sido dedicado às questões que moldam o território onde vivemos: a qualidade do ar, os espaços verdes, a forma como nos deslocamos, a energia que consumimos.</p>
      <p>Trabalho na Comissão Europeia desde 2016, onde acompanho start-ups inovadoras no European Innovation Council. Antes, coordenei prioridades europeias de I&amp;D em energia eólica e contribuí para instrumentos financeiros como o InnovFin. No Porto, coordenei o plano estratégico de ambiente da Área Metropolitana, fundei a ONG Campo Aberto, e co-apresentei o <em>Desafio Verde</em> na RTP2.</p>
    </section>

    <aside class="pullquote pullquote-alt">
      <blockquote>&laquo;O contributo dos cidadãos será, por assim dizer, a espinha dorsal de todo este processo.&raquo;</blockquote>
      <cite>— Futuro Sustentável, 2005</cite>
    </aside>

    <section class="links">
      <ul class="link-cards">
        <li><a href="https://www.linkedin.com/in/nquental" target="_blank">LinkedIn</a></li>
        <li><a href="https://scholar.google.com/citations?user=NoCUypYAAAAJ" target="_blank">Google Scholar</a></li>
      </ul>
    </section>

    <aside class="pullquote">
      <blockquote>&laquo;As crises são oportunidades para repensar decisões e realocar capital, usando-o de forma mais eficiente.&raquo;</blockquote>
      <cite>— Oportunidade para vencer a crise climática, 2020</cite>
    </aside>
  </main>

  <footer>
    <p><a href="https://www.linkedin.com/in/nquental" target="_blank">Nuno Quental</a> &copy; 2026</p>
  </footer>
</body>
</html>
'''

with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print('Generated index.html')
print('Done! (style.css is maintained separately)')

# CSS is now maintained as a separate file, not generated here
import sys; sys.exit(0)

# --- DEPRECATED Generate style.css ---
css = '''/* Nuno Quental — Portfolio */
:root {
  --text: #2c2c2c;
  --bg: #fafafa;
  --accent: #1a5276;
  --accent-light: #2980b9;
  --border: #e0e0e0;
  --muted: #666;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
  color: var(--text);
  background: var(--bg);
  line-height: 1.7;
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* Nav */
header { margin-bottom: 2.5rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
nav { display: flex; gap: 1.5rem; }
nav a {
  text-decoration: none;
  color: var(--muted);
  font-size: 0.95rem;
  letter-spacing: 0.03em;
  transition: color 0.2s;
}
nav a:hover, nav a.active { color: var(--accent); }

/* Hero */
.hero {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2.5rem;
}
.hero-text { flex: 1; }
.portrait {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--border);
}
h1 { font-size: 2rem; color: var(--accent); margin-bottom: 0.3rem; }
.tagline { font-style: italic; color: var(--muted); font-size: 1.05rem; }

/* Bio */
.bio { margin-bottom: 2.5rem; }
.bio h2 { font-size: 1.3rem; color: var(--accent); margin-bottom: 1rem; }
.bio p { margin-bottom: 1rem; text-align: justify; }

/* Links */
.links h2 { font-size: 1.3rem; color: var(--accent); margin-bottom: 0.8rem; }
.links ul { list-style: none; }
.links li { margin-bottom: 0.5rem; }
.links a {
  color: var(--accent-light);
  text-decoration: none;
  border-bottom: 1px dotted var(--accent-light);
}
.links a:hover { color: var(--accent); }

/* Publicações page */
.intro { font-style: italic; color: var(--muted); margin-bottom: 1.5rem; }
.toc {
  background: #f0f4f7;
  padding: 1rem 1.2rem;
  border-radius: 6px;
  margin-bottom: 2.5rem;
  line-height: 2;
}
.toc strong { display: block; margin-bottom: 0.3rem; color: var(--accent); }
.toc a {
  color: var(--accent-light);
  text-decoration: none;
  margin-right: 1rem;
  white-space: nowrap;
}
.toc a:hover { text-decoration: underline; }

section { margin-bottom: 2.5rem; }
section h2 {
  font-size: 1.3rem;
  color: var(--accent);
  border-bottom: 2px solid var(--accent);
  padding-bottom: 0.3rem;
  margin-bottom: 1.2rem;
}

/* Publication list */
ol.publications {
  list-style: none;
  counter-reset: pub;
}
ol.publications li {
  margin-bottom: 1.2rem;
  padding-left: 0;
  text-align: justify;
  line-height: 1.6;
}
.pdf-link, .doi-link {
  display: inline-block;
  font-size: 0.8rem;
  font-family: -apple-system, "Segoe UI", sans-serif;
  text-decoration: none;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  margin-left: 0.3rem;
  vertical-align: middle;
}
.pdf-link {
  background: #e74c3c;
  color: #fff;
}
.pdf-link:hover { background: #c0392b; }
.doi-link {
  background: var(--accent-light);
  color: #fff;
}
.doi-link:hover { background: var(--accent); }

/* Footer */
footer {
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
}

/* Responsive */
@media (max-width: 600px) {
  body { padding: 1rem; }
  .hero { flex-direction: column; text-align: center; }
  .portrait { width: 140px; height: 140px; }
  h1 { font-size: 1.6rem; }
  .toc a { display: block; margin-right: 0; }
}
'''

with open(os.path.join(SITE, 'style.css'), 'w', encoding='utf-8') as f:
    f.write(css)
print('Generated style.css')
