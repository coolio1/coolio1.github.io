"""Zotero data loading, categorisation and HTML rendering utilities for CV site."""

import os
import json
import re

SITE = r"C:\Users\quent\Downloads\Claude\CV"
EXPORT = r"C:\Users\quent\Zotero\export.json"
PDFS_DIR = os.path.join(SITE, "pdfs")
COVERS_DIR = os.path.join(SITE, "covers")

# Manual date overrides for items with missing/wrong dates in Zotero
DATE_OVERRIDES = {
    55: "2009",  # Naturbanization
    97: "2015",  # Changing the future of energy
    99: "2006",  # Plano Estratégico Ponte da Barca
    96: "2003",  # Portuguese environmental policy (conference)
}

# IDs classified as Cidade, Urbanismo e Espaços Verdes
CITY_IDS = {
    182,
    177,
    168,
    167,
    166,
    185,
    162,
    161,
    190,
    188,
    184,
    163,
    174,
    205,
    201,
    173,
    181,
    246,
    248,
}
# IDs classified as Mobilidade e Transportes
MOBILITY_IDS = {178, 172, 164, 202, 204}
# IDs classified as Trabalhos Universitários
UNIVERSITY_IDS = {49, 76, 165, 255, 256, 257}

# IDs forced into "trabalhos" regardless of Zotero type
TRABALHOS_IDS = {
    217
}  # Box 7.3 Changwon (bookSection in Zotero but relatório técnico no site)


def load_items() -> list:
    """Load items from Zotero export, apply date overrides and exclusion filters."""
    with open(EXPORT, "r", encoding="utf-8") as f:
        items = json.load(f)

    for item in items:
        if item["itemID"] in DATE_OVERRIDES and not item.get("date"):
            item["date"] = DATE_OVERRIDES[item["itemID"]]

    exclude_ids = set()
    for item in items:
        t = (item.get("title") or "").lower()
        if "carta" in t and "polici" in t:
            exclude_ids.add(item["itemID"])
        if "acknowledgement to reviewers" in t or "agradecimento aos reviewers" in t:
            exclude_ids.add(item["itemID"])
        if item["itemID"] == 229:  # Terraços - Livro Rio Fernandes
            exclude_ids.add(item["itemID"])
        if item["itemID"] == 246:  # A envolvente da Casa da Música - duplicado
            exclude_ids.add(item["itemID"])

    return [i for i in items if i["itemID"] not in exclude_ids]


def extract_year(date_str: str) -> str:
    if not date_str:
        return ""
    m = re.search(r"(\d{4})", date_str)
    return m.group(1) if m else ""


def format_authors_apa(creators: list) -> str:
    """Format author list in APA 7 style."""
    authors = [c for c in creators if c["type"] == "author"]
    if not authors:
        return ""
    parts = []
    for a in authors:
        last = a["last"]
        first = a["first"]
        if not first:
            parts.append(last)
        else:
            initials = " ".join([n[0] + "." for n in first.split() if n])
            parts.append(f"{last}, {initials}")
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} & {parts[1]}"
    else:
        return ", ".join(parts[:-1]) + ", & " + parts[-1]


def format_apa(item: dict) -> str:
    """Generate APA 7 citation HTML string."""
    authors = format_authors_apa(item.get("creators", []))
    year = extract_year(item.get("date"))
    title = item.get("title", "")
    typ = item.get("typeName", "")
    pub = item.get("publicationTitle") or ""
    book = item.get("bookTitle") or ""
    vol = item.get("volume") or ""
    iss = item.get("issue") or ""
    pages = item.get("pages") or ""
    doi = item.get("doi") or ""
    publisher = item.get("publisher") or ""
    place = item.get("place") or ""
    institution = item.get("institution") or ""
    conf = item.get("conferenceName") or ""
    proc = item.get("proceedingsTitle") or ""
    isbn = item.get("ISBN") or ""
    university = item.get("university") or ""
    thesis_type = item.get("thesisType") or ""

    year_str = f"({year})" if year else "(s.d.)"

    if typ == "journalArticle":
        title_end = "." if not title.endswith(("?", "!")) else ""
        ref = f"{authors} {year_str}. {title}{title_end}"
        if pub:
            ref += f" <em>{pub}</em>"
            if vol:
                ref += f", <em>{vol}</em>"
            if iss:
                ref += f"({iss})" if vol else f" ({iss})"
            if pages:
                ref += f", {pages}"
            ref += "."
        if doi:
            doi_url = f"https://doi.org/{doi}"
            ref += f' <a href="{doi_url}" target="_blank">{doi_url}</a>'

    elif typ == "bookSection":
        editors = [c for c in item.get("creators", []) if c["type"] == "editor"]
        ed_str = ""
        if editors:
            ed_parts = [
                f"{e['first'][0]}. {e['last']}" if e["first"] else e["last"]
                for e in editors
            ]
            ed_str = f" Em {', '.join(ed_parts)} (Ed.),"
        title_end = "." if not title.endswith((".", "?", "!")) else ""
        ref = f"{authors} {year_str}. {title}{title_end}{ed_str}"
        if book:
            ref += f" <em>{book}</em>"
        if pages:
            ref += f" (pp. {pages})"
        ref += "."
        if publisher:
            ref += f" {publisher}"
        if place:
            ref += f", {place}"
        if (publisher or place) and not ref.endswith("."):
            ref += "."

    elif typ == "thesis":
        ref = f"{authors} {year_str}. <em>{title}</em>"
        if thesis_type:
            ref += f" [{thesis_type}]"
        ref += "."
        if university:
            ref += f" {university}"
        if place:
            ref += f", {place}"
        if (university or place) and not ref.endswith("."):
            ref += "."

    elif typ == "report":
        editors = [c for c in item.get("creators", []) if c["type"] == "editor"]
        ref = f"{authors} {year_str}. <em>{title}</em>."
        if editors:
            ed_parts = [
                f"{e['first'][0]}. {e['last']}" if e["first"] else e["last"]
                for e in editors
            ]
            ref += f" Coordenação de {', '.join(ed_parts)}."
        if institution:
            ref += f" {institution}"
        elif publisher:
            ref += f" {publisher}"
        if place:
            ref += f", {place}"
        if (institution or publisher or place) and not ref.endswith("."):
            ref += "."

    elif typ in ("newspaperArticle", "magazineArticle"):
        title_end = "." if not title.endswith(("?", "!")) else ""
        ref = f"{authors} {year_str}. {title}{title_end}"
        if pub:
            ref += f" <em>{pub}</em>"
            if vol:
                ref += f", <em>{vol}</em>"
            if iss:
                ref += f"({iss})" if vol else f" ({iss})"
            if pages:
                ref += f", {pages}"
            ref += "."

    elif typ == "conferencePaper":
        title_end = "." if not title.endswith(("?", "!")) else ""
        ref = f"{authors} {year_str}. {title}{title_end}"
        if proc:
            ref += f" Em <em>{proc}</em>"
            if pages:
                ref += f" (pp. {pages})"
            ref += "."
        elif conf:
            ref += f" <em>{conf}</em>"
            if place:
                ref += f", {place}"
            if pages:
                ref += f" (pp. {pages})"
            ref += "."
        if publisher and not proc:
            ref += f" {publisher}"
            if not ref.endswith("."):
                ref += "."
        if isbn:
            ref += f" ISBN {isbn}."

    else:
        title_end = "." if not title.endswith(("?", "!")) else ""
        ref = f"{authors} {year_str}. {title}{title_end}"

    return ref


def get_cover_filename(item: dict) -> str | None:
    """Find cover image filename for this item, or None."""
    import unicodedata

    for att in item.get("attachments", []):
        basename = os.path.basename(att)
        jpg_name = os.path.splitext(basename)[0] + ".jpg"
        if os.path.exists(os.path.join(COVERS_DIR, jpg_name)):
            return jpg_name
        ascii_name = (
            unicodedata.normalize("NFD", jpg_name).encode("ascii", "ignore").decode()
        )
        if os.path.exists(os.path.join(COVERS_DIR, ascii_name)):
            return ascii_name
    return None


def get_pdf_filename(item: dict) -> str | None:
    """Find PDF filename for this item in pdfs/, or None."""
    import unicodedata

    for att in item.get("attachments", []):
        basename = os.path.basename(att)
        pdf_name = os.path.splitext(basename)[0] + ".pdf"
        if os.path.exists(os.path.join(PDFS_DIR, pdf_name)):
            return pdf_name
        if os.path.exists(os.path.join(PDFS_DIR, basename)):
            return basename
        ascii_name = (
            unicodedata.normalize("NFD", pdf_name).encode("ascii", "ignore").decode()
        )
        if os.path.exists(os.path.join(PDFS_DIR, ascii_name)):
            return ascii_name
    return None


def categorize(item: dict) -> str:
    """Return category key for item."""
    typ = item.get("typeName", "")
    title = (item.get("title") or "").lower()
    atts = " ".join(item.get("attachments", []))

    if item.get("itemID") in UNIVERSITY_IDS:
        return "universitario"
    if item.get("itemID") in TRABALHOS_IDS:
        return "trabalhos"
    if typ == "thesis":
        return "tese_lic" if item.get("itemID") == 81 else "tese"
    elif typ in ("journalArticle", "bookSection", "conferencePaper"):
        return "cientifico"
    elif typ in ("report", "magazineArticle"):
        return "trabalhos"
    elif typ == "newspaperArticle":
        iid = item.get("itemID")
        if "polici" in title or "inspector" in title or "4 faces" in title:
            return "policiario"
        if "COVID" in atts or "covid" in title:
            return "op_covid"
        if iid in MOBILITY_IDS:
            return "op_mobilidade"
        if iid in CITY_IDS:
            return "op_cidade"
        return "op_ambiente"
    else:
        return "outros"


def build_categories(items: list) -> dict:
    """Group and sort items into category buckets."""
    categories: dict = {
        "tese": [],
        "tese_lic": [],
        "cientifico": [],
        "universitario": [],
        "trabalhos": [],
        "op_cidade": [],
        "op_ambiente": [],
        "op_mobilidade": [],
        "op_covid": [],
        "policiario": [],
    }
    for item in items:
        cat = categorize(item)
        categories.setdefault(cat, []).append(item)
    for cat in categories:
        categories[cat].sort(
            key=lambda x: extract_year(x.get("date", "")) or "0000", reverse=True
        )
    return categories


def render_items(
    items_list: list, show_covers: bool = False, show_year_markers: bool = False
) -> str:
    """Render a list of items as HTML <li> elements."""
    html = ""
    last_year = None
    for item in items_list:
        year = extract_year(item.get("date", ""))
        if show_year_markers and year and year != last_year:
            html += f'        <li class="year-marker" aria-hidden="true"><span>{year}</span></li>\n'
            last_year = year
        apa = format_apa(item)
        pdf = get_pdf_filename(item)
        cover = get_cover_filename(item) if show_covers else None
        url = item.get("url")
        pdf_badge = (
            f' <a href="pdfs/{pdf}" class="pdf-link" title="Descarregar PDF" target="_blank">PDF</a>'
            if pdf
            else ""
        )
        url_badge = (
            f' <a href="{url}" class="url-link" title="Ver online" target="_blank">URL</a>'
            if url
            else ""
        )
        badges = pdf_badge + url_badge
        if cover and pdf:
            html += (
                f'        <li class="has-cover">'
                f'<a href="pdfs/{pdf}" target="_blank" class="cover-thumb">'
                f'<img src="covers/{cover}" alt="" loading="lazy"></a>'
                f"<div>{apa}{badges}</div></li>\n"
            )
        else:
            html += f"        <li>{apa}{badges}</li>\n"
    return html


def render_featured(items_list: list) -> str:
    """Render featured items as card HTML."""
    html = ""
    for item in items_list:
        title = item.get("title", "")
        year = extract_year(item.get("date", ""))
        pdf = get_pdf_filename(item)
        cover = get_cover_filename(item)
        authors = format_authors_apa(item.get("creators", []))
        pub = item.get("publicationTitle") or item.get("publisher") or ""
        link = f"pdfs/{pdf}" if pdf else "#"
        cover_html = (
            f'<img src="covers/{cover}" alt="" loading="lazy">'
            if cover
            else '<div class="no-cover"></div>'
        )
        html += (
            f'      <a href="{link}" target="_blank" class="featured-card">\n'
            f'        <div class="featured-cover">{cover_html}</div>\n'
            f'        <div class="featured-info">\n'
            f'          <span class="featured-year">{year}</span>\n'
            f"          <h3>{title}</h3>\n"
            f"          <p>{authors}</p>\n"
            f'          <p class="featured-pub">{pub}</p>\n'
            f"        </div>\n"
            f"      </a>\n"
        )
    return html
