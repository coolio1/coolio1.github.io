#!/usr/bin/env python3
"""
Re-extract MPC (Movimento pelo Parque da Cidade) comunicados preserving HTML formatting.

Sources:
  - .doc files in Comunicados/ → win32com SaveAs filtered HTML
  - .html files in Sitio/comunicados/ → direct read
  - .pdf files in Comunicados/ → PyMuPDF fallback

Output: data/mpc_comunicados_html.json
"""

import json
import os
import re
import tempfile
from html import unescape

BASE_DIR = r"C:\Users\quent\OneDrive\Arquivo\Ambiente\Parque Cidade"
DATA_DIR = r"C:\Users\quent\Downloads\Claude\CV\data"

KEEP_TAGS = {
    "b",
    "i",
    "strong",
    "em",
    "u",
    "table",
    "tr",
    "td",
    "th",
    "thead",
    "tbody",
    "caption",
    "ul",
    "ol",
    "li",
    "p",
    "br",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "sup",
    "sub",
    "hr",
}

STRIP_WITH_CONTENT = {"script", "style", "map", "noscript"}

CP1252_MAP = {
    "\x80": "\u20ac",
    "\x82": "\u201a",
    "\x83": "\u0192",
    "\x84": "\u201e",
    "\x85": "\u2026",
    "\x86": "\u2020",
    "\x87": "\u2021",
    "\x88": "\u02c6",
    "\x89": "\u2030",
    "\x8a": "\u0160",
    "\x8b": "\u2039",
    "\x8c": "\u0152",
    "\x8e": "\u017d",
    "\x91": "\u2018",
    "\x92": "\u2019",
    "\x93": "\u201c",
    "\x94": "\u201d",
    "\x95": "\u2022",
    "\x96": "\u2013",
    "\x97": "\u2014",
    "\x98": "\u02dc",
    "\x99": "\u2122",
    "\x9a": "\u0161",
    "\x9b": "\u203a",
    "\x9c": "\u0153",
    "\x9e": "\u017e",
    "\x9f": "\u0178",
}


def read_file(filepath):
    """Read file with encoding fallback."""
    for enc in ["utf-8", "cp1252"]:
        try:
            with open(filepath, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(filepath, "r", encoding="cp1252", errors="replace") as f:
        return f.read()


def extract_body(html_text):
    """Extract <body> content."""
    m = re.search(r"<body[^>]*>(.*)</body>", html_text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return html_text


def clean_html(html_frag):
    """Clean HTML fragment following the same rules as Quercus extraction."""

    # Remove Office namespace tags (o:p, w:, st:, v:, etc.)
    html_frag = re.sub(r"</?[owv]:\w+[^>]*>", "", html_frag, flags=re.IGNORECASE)
    html_frag = re.sub(r"</?st\d?:\w+[^>]*>", "", html_frag, flags=re.IGNORECASE)

    # Remove XML declarations and processing instructions
    html_frag = re.sub(r"<\?xml[^>]*\?>", "", html_frag, flags=re.IGNORECASE)
    html_frag = re.sub(
        r"<!\[if[^]]*\]>.*?<!\[endif\]>", "", html_frag, flags=re.DOTALL | re.IGNORECASE
    )
    html_frag = re.sub(
        r"<!--\[if[^]]*\]>.*?<!\[endif\]-->",
        "",
        html_frag,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html_frag = re.sub(
        r"<!--\[if.*?-->", "", html_frag, flags=re.DOTALL | re.IGNORECASE
    )

    # Strip tags with content
    for tag in STRIP_WITH_CONTENT:
        html_frag = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}\s*>",
            "",
            html_frag,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # Remove img tags
    html_frag = re.sub(r"<img[^>]*/?>", "", html_frag, flags=re.IGNORECASE)

    # Remove HTML comments
    html_frag = re.sub(r"<!--.*?-->", "", html_frag, flags=re.DOTALL)

    # Remove <a> tags but keep link text
    html_frag = re.sub(
        r"<a\s[^>]*>(.*?)</a>",
        r"\1",
        html_frag,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html_frag = re.sub(r"<a\s[^>]*/?>", "", html_frag, flags=re.IGNORECASE)

    # Remove font tags (keep content)
    html_frag = re.sub(r"</?font[^>]*>", "", html_frag, flags=re.IGNORECASE)

    # Remove span tags (keep content)
    html_frag = re.sub(r"</?span[^>]*>", "", html_frag, flags=re.IGNORECASE)

    # Remove div tags (keep content)
    html_frag = re.sub(r"</?div[^>]*>", "", html_frag, flags=re.IGNORECASE)

    # Process remaining tags: keep only allowed, strip attributes
    def clean_tag(match):
        tag_full = match.group(0)
        tag_name_m = re.match(r"<(/?\w+)", tag_full)
        if not tag_name_m:
            return tag_full
        raw = tag_name_m.group(1)
        is_closing = raw.startswith("/")
        tag_name = raw.lstrip("/").lower()

        if tag_name not in KEEP_TAGS:
            return ""

        # For table cells, keep colspan/rowspan
        if tag_name in ("td", "th", "tr"):
            attrs = []
            for attr in ["colspan", "rowspan"]:
                am = re.search(
                    rf'{attr}\s*=\s*["\']?(\d+)["\']?', tag_full, re.IGNORECASE
                )
                if am and am.group(1) != "1":
                    attrs.append(f'{attr}="{am.group(1)}"')
            if is_closing:
                return f"</{tag_name}>"
            if attrs:
                return f"<{tag_name} {' '.join(attrs)}>"
            return f"<{tag_name}>"

        if is_closing:
            return f"</{tag_name}>"
        if tag_name in ("br", "hr"):
            return f"<{tag_name}>"
        return f"<{tag_name}>"

    html_frag = re.sub(r"<[^>]+>", clean_tag, html_frag)

    # Decode HTML entities
    html_frag = unescape(html_frag)

    # Fix cp1252 control chars
    for old_c, new_c in CP1252_MAP.items():
        html_frag = html_frag.replace(old_c, new_c)

    # Non-breaking space → space
    html_frag = html_frag.replace("\xa0", " ")

    # Whitespace cleanup
    html_frag = re.sub(r"[ \t]+", " ", html_frag)
    html_frag = re.sub(r"\n\s*\n", "\n", html_frag)
    lines = [line.strip() for line in html_frag.split("\n")]
    html_frag = "\n".join(line for line in lines if line)

    # Remove empty tags
    for tag in [
        "p",
        "b",
        "i",
        "em",
        "strong",
        "li",
        "td",
        "tr",
        "table",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    ]:
        html_frag = re.sub(rf"<{tag}>\s*</{tag}>", "", html_frag)

    html_frag = re.sub(r"\n\s*\n", "\n", html_frag)
    return html_frag.strip()


def convert_doc_to_html(doc_path, word_app):
    """Convert .doc to filtered HTML via win32com, return clean HTML string."""
    tmp_dir = tempfile.mkdtemp()
    tmp_html = os.path.join(tmp_dir, "output.html")

    try:
        doc = word_app.Documents.Open(doc_path, ReadOnly=True)
        # FileFormat=10 is wdFormatFilteredHTML
        doc.SaveAs(tmp_html, FileFormat=10)
        doc.Close(False)

        raw = read_file(tmp_html)
        body = extract_body(raw)
        return clean_html(body), None
    except Exception as e:
        return None, f"DOC conversion failed: {e}"
    finally:
        # Clean up temp files
        for f in os.listdir(tmp_dir):
            try:
                fp = os.path.join(tmp_dir, f)
                if os.path.isfile(fp):
                    os.remove(fp)
            except Exception:
                pass
        # Also clean up _files folder that Word creates
        files_dir = os.path.join(tmp_dir, "output_files")
        if os.path.isdir(files_dir):
            import shutil

            try:
                shutil.rmtree(files_dir)
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass


def convert_html_source(html_path):
    """Read .html from Sitio and clean it."""
    try:
        raw = read_file(html_path)
        body = extract_body(raw)
        return clean_html(body), None
    except Exception as e:
        return None, f"HTML read failed: {e}"


def convert_pdf_to_html(pdf_path):
    """Extract text from PDF via PyMuPDF and wrap in basic HTML."""
    try:
        import fitz

        doc = fitz.open(pdf_path)
        paragraphs = []
        for page in doc:
            text = page.get_text()
            for para in text.split("\n\n"):
                para = para.strip()
                if para:
                    paragraphs.append(f"<p>{para}</p>")
        doc.close()
        html = "\n".join(paragraphs)
        return html if html else None, None if html else "PDF empty"
    except Exception as e:
        return None, f"PDF extraction failed: {e}"


def main():
    input_path = os.path.join(DATA_DIR, "mpc_comunicados.json")
    output_path = os.path.join(DATA_DIR, "mpc_comunicados_html.json")

    with open(input_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} comunicados from mpc_comunicados.json")

    # Initialize Word
    import win32com.client

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0  # wdAlertsNone

    results = []
    errors = []
    source_stats = {"doc": 0, "html": 0, "pdf": 0, "failed": 0}

    for i, item in enumerate(items):
        source = item["source_file"]
        date = item["date"]
        title = item["title"]
        html_content = None
        error = None

        print(f"  [{i + 1}/{len(items)}] {date} - {title}")

        # Determine source type and path
        if source.endswith(".doc"):
            doc_path = os.path.join(BASE_DIR, "Comunicados", source)
            if os.path.exists(doc_path):
                html_content, error = convert_doc_to_html(doc_path, word)
                if html_content:
                    source_stats["doc"] += 1
                    print(f"         → DOC OK ({len(html_content)} chars)")

            if not html_content:
                # Try .html from Sitio
                # Map date to Sitio filename patterns
                html_fallback = find_sitio_html(date)
                if html_fallback:
                    html_content, error2 = convert_html_source(html_fallback)
                    if html_content:
                        source_stats["html"] += 1
                        error = None
                        print(
                            f"         → HTML fallback OK ({len(html_content)} chars)"
                        )
                    else:
                        error = f"{error}; {error2}"

            if not html_content:
                # Try .pdf
                pdf_path = doc_path.replace(".doc", ".pdf")
                if os.path.exists(pdf_path):
                    html_content, error3 = convert_pdf_to_html(pdf_path)
                    if html_content:
                        source_stats["pdf"] += 1
                        error = None
                        print(f"         → PDF fallback OK ({len(html_content)} chars)")
                    else:
                        error = f"{error}; {error3}"

        elif source.startswith("Sitio/"):
            html_path = os.path.join(BASE_DIR, source)
            if os.path.exists(html_path):
                html_content, error = convert_html_source(html_path)
                if html_content:
                    source_stats["html"] += 1
                    print(f"         → HTML OK ({len(html_content)} chars)")

            if not html_content:
                # Try to find matching .doc
                doc_fallback = find_doc_for_date(date)
                if doc_fallback:
                    html_content, error2 = convert_doc_to_html(doc_fallback, word)
                    if html_content:
                        source_stats["doc"] += 1
                        error = None
                        print(f"         → DOC fallback OK ({len(html_content)} chars)")

        if not html_content:
            source_stats["failed"] += 1
            errors.append(f"[{i}] {date} - {title}: {error}")
            html_content = ""
            print(f"         → FAILED: {error}")

        results.append(
            {
                "date": date,
                "title": title,
                "html": html_content,
                "source_file": source,
            }
        )

    # Close Word
    word.Quit()
    print("\nWord closed.")

    # Sort by date
    results.sort(key=lambda x: x["date"])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n=== Results ===")
    print(f"Total: {len(results)} comunicados")
    print(f"  DOC: {source_stats['doc']}")
    print(f"  HTML: {source_stats['html']}")
    print(f"  PDF: {source_stats['pdf']}")
    print(f"  Failed: {source_stats['failed']}")
    print(f"Written to: {output_path}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")


def find_sitio_html(date):
    """Try to find a matching .html in Sitio/comunicados/ for a given date."""
    sitio_dir = os.path.join(BASE_DIR, "Sitio", "comunicados")
    if not os.path.isdir(sitio_dir):
        return None

    # Date is YYYY-MM-DD
    parts = date.split("-")
    if len(parts) != 3:
        return None
    year, month, day = parts

    # Known month names (Portuguese)
    month_names = {
        "01": "janeiro",
        "02": "fevereiro",
        "03": "marco",
        "04": "abril",
        "05": "maio",
        "06": "junho",
        "07": "julho",
        "08": "agosto",
        "09": "setembro",
        "10": "outubro",
        "11": "novembro",
        "12": "novembro",
    }
    # Also short forms
    month_short = {
        "01": "jan",
        "02": "fev",
        "03": "mar",
        "04": "abr",
        "05": "mai",
        "06": "jun",
        "07": "jul",
        "08": "ago",
        "09": "set",
        "10": "out",
        "11": "nov",
        "12": "nov",
    }

    day_int = str(int(day))  # remove leading zero

    # Try patterns like: 03outubro2001.html, 14jul2001.html, etc.
    for f in os.listdir(sitio_dir):
        if not f.endswith(".html"):
            continue
        fl = f.lower()
        if year in fl and (day_int in fl[:3] or day in fl[:3]):
            return os.path.join(sitio_dir, f)

    return None


def find_doc_for_date(date):
    """Try to find a .doc file matching a date."""
    com_dir = os.path.join(BASE_DIR, "Comunicados")
    if not os.path.isdir(com_dir):
        return None
    prefix = date + " - "
    for f in os.listdir(com_dir):
        if f.startswith(prefix) and f.endswith(".doc"):
            return os.path.join(com_dir, f)
    return None


if __name__ == "__main__":
    main()
