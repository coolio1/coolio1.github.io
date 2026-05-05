"""Generate the full academic portfolio site from Zotero export data."""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from site_data import (  # noqa: E402
    PDFS_DIR,
    SITE,
    build_categories,
    load_items,
    render_featured,
    render_items,
)

items = load_items()

# Categorize all items
categories = build_categories(items)

# Count totals
total = sum(len(v) for v in categories.values())
print(f"Total items for site: {total}")
for cat, items_list in categories.items():
    print(f"  {cat}: {len(items_list)}")

# --- Generate escritos.html ---

# Consolidated structure: 5 top-level sections, opinion has subsections
top_sections = [
    {
        "id": "teses",
        "label": "Teses",
        "subs": [
            ("Doutoramento", categories.get("tese", [])),
            ("Licenciatura", categories.get("tese_lic", [])),
        ],
    },
    {
        "id": "cientifico",
        "label": "Artigos Científicos",
        "subs": [("", categories.get("cientifico", []))],
    },
    {
        "id": "trabalhos",
        "label": "Relatórios Técnicos",
        "nav_label": "Relatórios",
        "subs": [("", categories.get("trabalhos", []))],
    },
    {
        "id": "opiniao",
        "label": "Artigos de Opinião",
        "subs": [
            ("Cidade, Urbanismo e Espaços Verdes", categories.get("op_cidade", [])),
            ("Ambiente e Sustentabilidade", categories.get("op_ambiente", [])),
            ("Mobilidade e Transportes", categories.get("op_mobilidade", [])),
            ("COVID-19", categories.get("op_covid", [])),
        ],
    },
    {
        "id": "policiario",
        "label": "Ficção Policial",
        "subs": [("", categories.get("policiario", []))],
    },
    {
        "id": "universitario",
        "label": "Trabalhos Universitários",
        "nav_label": "Universidade",
        "subs": [("", categories.get("universitario", []))],
    },
]

# Sections with covers: trabalhos, teses, cientifico
SECTIONS_WITH_COVERS = {"teses", "universitario", "trabalhos", "cientifico"}
# Sections with year markers: opiniao (many items)
SECTIONS_WITH_YEARS = {"opiniao"}

escritos_sections = ""
for sec in top_sections:
    total_in_sec = sum(len(s[1]) for s in sec["subs"])
    if total_in_sec == 0:
        continue
    show_covers = sec["id"] in SECTIONS_WITH_COVERS
    show_years = sec["id"] in SECTIONS_WITH_YEARS
    escritos_sections += f'    <section id="{sec["id"]}">\n'
    escritos_sections += f"      <h2>{sec['label']}</h2>\n"
    for sub_label, sub_items in sec["subs"]:
        if not sub_items:
            continue
        if sub_label:
            escritos_sections += f"      <h3>{sub_label}</h3>\n"
        escritos_sections += '      <ol class="publications">\n'
        escritos_sections += render_items(
            sub_items, show_covers=show_covers, show_year_markers=show_years
        )
        escritos_sections += "      </ol>\n"
    escritos_sections += "    </section>\n\n"

# Escolares section (Porto Editora PDFs — not from Zotero)
ESCOLARES_DIR = os.path.join(PDFS_DIR, "Porto Editora")
ESCOLARES_EXCLUDE = {"as-dunas.pdf"}  # superseded by as-dunas-v2.pdf

ESCOLARES_TITLES = {
    "a-vida.pdf": "A vida",
    "agricultura-e-diversidade.pdf": "Agricultura e diversidade",
    "agricultura-e-domesticacao.pdf": "Agricultura e domesticação",
    "animais-vs-plantas.pdf": "Animais vs. plantas",
    "as-dunas-v2.pdf": "As dunas",
    "aves-nas-cidades.pdf": "Aves nas cidades",
    "biomas-e-factores-abioticos.pdf": "Biomas e factores abióticos",
    "biotecnologia.pdf": "Biotecnologia",
    "clima-e-ecossistemas.pdf": "Clima e ecossistemas",
    "clima-esta-a-mudar.pdf": "O clima está a mudar",
    "construir-ninhos.pdf": "Construir ninhos",
    "descobrindo-o-litoral.pdf": "Descobrindo o litoral",
    "diversidade-da-vida.pdf": "Diversidade da vida",
    "ecossistemas.pdf": "Ecossistemas",
    "escola-ecologica.pdf": "Escola ecológica",
    "estrutura-das-plantas.pdf": "Estrutura das plantas",
    "fazer-um-charco.pdf": "Fazer um charco",
    "floresta-na-escola.pdf": "Floresta na escola",
    "fontes-energeticas.pdf": "Fontes energéticas",
    "golfinhos-do-sado.pdf": "Golfinhos do Sado",
    "homem-e-biodiversidade.pdf": "Homem e biodiversidade",
    "inspeccoes-costeiras.pdf": "Inspecções costeiras",
    "o-lobo.pdf": "O lobo",
    "poluicao-do-ar.pdf": "Poluição do ar",
    "predacao-e-mimetismo.pdf": "Predação e mimetismo",
    "residuos-e-reciclagem.pdf": "Resíduos e reciclagem",
    "sabias-que-natureza.pdf": "Sabias que… (natureza)",
    "sabias-que-reciclagem.pdf": "Sabias que… (reciclagem)",
    "salvar-os-oceanos.pdf": "Salvar os oceanos",
    "solo-e-rochas.pdf": "Solo e rochas",
    "vida-em-perigo.pdf": "Vida em perigo",
    "vida-nas-cidades-cont.pdf": "Vida nas cidades (cont.)",
    "vida-nas-cidades.pdf": "Vida nas cidades",
}

escolares_files = sorted(
    [
        f
        for f in os.listdir(ESCOLARES_DIR)
        if f.endswith(".pdf") and f not in ESCOLARES_EXCLUDE
    ],
    key=lambda f: ESCOLARES_TITLES.get(f, f).lower(),
)
escolares_section = '    <section id="escolares">\n'
escolares_section += "      <h2>Textos Didácticos</h2>\n"
escolares_section += '      <ol class="publications">\n'
for f in escolares_files:
    title = ESCOLARES_TITLES.get(f, f.replace("-", " ").replace(".pdf", "").title())
    href = f"pdfs/Porto Editora/{f}"
    escolares_section += f'        <li>{title} <a href="{href}" class="pdf-link" title="Descarregar PDF" target="_blank">PDF</a></li>\n'
escolares_section += "      </ol>\n"
escolares_section += "    </section>\n\n"
escritos_sections += escolares_section

# Featured items (destaques)
FEATURED_IDS = [
    79,
    59,
    57,
    58,
    55,
    100,
]  # Tese, Scientometrics, Env Dev Sust, Sust Dev, Naturbanization, SET Plan
featured_items = [item for item in items if item["itemID"] in FEATURED_IDS]
featured_items.sort(key=lambda x: FEATURED_IDS.index(x["itemID"]))

toc_pills = "\n".join(
    [
        f'        <a href="#{sec["id"]}">{sec.get("nav_label", sec["label"])}</a>'
        for sec in top_sections
        if sum(len(s[1]) for s in sec["subs"]) > 0
    ]
)
toc_pills += '\n        <a href="#escolares">Didácticos</a>'
total_items = sum(sum(len(s[1]) for s in sec["subs"]) for sec in top_sections) + len(
    escolares_files
)

escritos_html = f"""<!DOCTYPE html>
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
"""

with open(os.path.join(SITE, "escritos.html"), "w", encoding="utf-8") as f:
    f.write(escritos_html)
print("Generated escritos.html")

# --- Generate index.html ---
index_html = """<!DOCTYPE html>
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
  {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Nuno Quental",
    "jobTitle": "Engenheiro do Ambiente",
    "description": "Investigador em sustentabilidade urbana e engenheiro do ambiente.",
    "url": "https://coolio1.github.io/",
    "image": "https://coolio1.github.io/nuno.jpg",
    "affiliation": {
      "@type": "Organization",
      "name": "Comissão Europeia"
    },
    "sameAs": [
      "https://www.linkedin.com/in/nquental",
      "https://scholar.google.com/citations?user=NoCUypYAAAAJ"
    ]
  }
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
"""

with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("Generated index.html")
print("Done! (style.css is maintained separately)")

sys.exit(0)
