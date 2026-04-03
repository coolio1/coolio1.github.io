#!/usr/bin/env python3
"""
Re-extract Quercus comunicados and paginas preserving HTML formatting.
Reads from original .htm files, outputs clean HTML fragments.
"""

import json
import re
import os
from html import unescape

BASE_DIR = r"C:\Users\quent\OneDrive\Arquivo\Ambiente\Quercus"
DATA_DIR = r"C:\Users\quent\Downloads\Claude\CV\data"

# Tags to preserve (content formatting)
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
    "a",
    "sup",
    "sub",
    "hr",
    "div",
    "font",  # will keep for now, some have color info
}

# Tags to strip entirely (including content)
STRIP_WITH_CONTENT = {"script", "style", "map", "noscript"}


def read_file(filepath):
    """Read file with proper encoding handling.
    Try cp1252 before iso-8859-1 because cp1252 properly maps bytes 0x80-0x9F
    to characters like en-dash, em-dash, smart quotes, etc."""
    for enc in ["utf-8", "cp1252"]:
        try:
            with open(filepath, "r", encoding=enc, errors="strict") as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    # Fallback: cp1252 with replacement
    with open(filepath, "r", encoding="cp1252", errors="replace") as f:
        return f.read()


def extract_body_content(html_text):
    """Extract the main content area from the HTML page."""

    # Strategy 1: Look for BeginEditable "corpo"
    pattern1 = r'<!--\s*#BeginEditable\s+"corpo"\s*-->(.*?)<!--\s*#EndEditable'
    match = re.search(pattern1, html_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Strategy 2: Look for div layers with content (old Quercus pages)
    # These pages use absolutely positioned divs
    # Try to get content from body, excluding navigation
    body_match = re.search(
        r"<body[^>]*>(.*)</body>", html_text, re.DOTALL | re.IGNORECASE
    )
    if body_match:
        return body_match.group(1).strip()

    # Strategy 3: Just return everything
    return html_text


def clean_html_fragment(html_fragment):
    """Clean HTML fragment: keep formatting tags, remove navigation/layout."""

    # Remove script/style tags with content
    for tag in STRIP_WITH_CONTENT:
        html_fragment = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}\s*>",
            "",
            html_fragment,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # Remove map tags with content
    html_fragment = re.sub(
        r"<map[^>]*>.*?</map\s*>", "", html_fragment, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove image tags (navigation images, shims, etc.)
    html_fragment = re.sub(r"<img[^>]*>", "", html_fragment, flags=re.IGNORECASE)

    # Remove area tags
    html_fragment = re.sub(r"<area[^>]*>", "", html_fragment, flags=re.IGNORECASE)

    # Remove Dreamweaver comments and template markers
    html_fragment = re.sub(r"<!--\s*#(?:Begin|End)\w+[^>]*-->", "", html_fragment)
    html_fragment = re.sub(
        r"<mm:editable>.*?</mm:editable>",
        "",
        html_fragment,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove HTML comments
    html_fragment = re.sub(r"<!--.*?-->", "", html_fragment, flags=re.DOTALL)

    # Process <a> tags: keep text but remove href (to avoid broken links)
    # Convert <a href="...">text</a> to just text
    html_fragment = re.sub(
        r"<a\s[^>]*>(.*?)</a>", r"\1", html_fragment, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove standalone <a> tags
    html_fragment = re.sub(r"<a\s[^>]*/>", "", html_fragment, flags=re.IGNORECASE)

    # Remove layout table structure but keep content tables
    # Layout tables typically have navigation images, shims, etc.
    # We'll use a heuristic: remove table/tr/td that are at the outermost level
    # if they contain navigation elements

    # Remove font tags but keep content (font is mostly decorative)
    # Actually, some font tags have meaningful color for headers
    # Let's strip font tags but keep their content
    html_fragment = re.sub(r"<font[^>]*>", "", html_fragment, flags=re.IGNORECASE)
    html_fragment = re.sub(r"</font\s*>", "", html_fragment, flags=re.IGNORECASE)

    # Remove span tags (mostly CSS class references)
    html_fragment = re.sub(r"<span[^>]*>", "", html_fragment, flags=re.IGNORECASE)
    html_fragment = re.sub(r"</span\s*>", "", html_fragment, flags=re.IGNORECASE)

    # Remove class, style, align, width, height, border, cellpadding, cellspacing,
    # bgcolor, color, valign, colspan, rowspan attributes from remaining tags
    # But keep colspan/rowspan for tables
    def clean_tag_attrs(match):
        tag_full = match.group(0)
        # Extract tag name
        tag_name_match = re.match(r"<(/?\w+)", tag_full)
        if not tag_name_match:
            return tag_full
        tag_name = tag_name_match.group(1).lower().lstrip("/")

        if tag_name not in KEEP_TAGS:
            # Remove entire tag if not in keep list
            return ""

        # For table-related tags, keep colspan and rowspan
        if tag_name in ("td", "th", "tr"):
            attrs = []
            for attr in ["colspan", "rowspan"]:
                attr_match = re.search(
                    rf'{attr}\s*=\s*["\']?(\d+)["\']?', tag_full, re.IGNORECASE
                )
                if attr_match and attr_match.group(1) != "1":
                    attrs.append(f'{attr}="{attr_match.group(1)}"')
            if attrs:
                return f"<{tag_name} {' '.join(attrs)}>"
            return f"<{tag_name}>"

        # For all other tags, strip all attributes
        is_closing = tag_full.startswith("</")
        is_self_closing = tag_full.rstrip().endswith("/>")

        if is_closing:
            return f"</{tag_name}>"
        elif tag_name == "br":
            return "<br>"
        elif tag_name == "hr":
            return "<hr>"
        else:
            return f"<{tag_name}>"

    # Process all tags
    html_fragment = re.sub(r"<[^>]+>", clean_tag_attrs, html_fragment)

    # Remove div tags that are just wrappers (but keep content)
    html_fragment = re.sub(r"<div>", "", html_fragment)
    html_fragment = re.sub(r"</div>", "", html_fragment)

    # Decode HTML entities to proper characters
    html_fragment = unescape(html_fragment)

    # Re-encode the essential HTML entities
    # We need to be careful: & must be encoded, but not double-encode
    # Actually for JSON storage, we can keep unicode characters
    # Only need to worry about < > & within text

    # Fix cp1252 control characters that may have been misread as iso-8859-1
    # These are Unicode codepoints 0x80-0x9F which should be cp1252 characters
    CP1252_MAP = {
        "\x80": "\u20ac",  # €
        "\x82": "\u201a",  # ‚
        "\x83": "\u0192",  # ƒ
        "\x84": "\u201e",  # „
        "\x85": "\u2026",  # …
        "\x86": "\u2020",  # †
        "\x87": "\u2021",  # ‡
        "\x88": "\u02c6",  # ˆ
        "\x89": "\u2030",  # ‰
        "\x8a": "\u0160",  # Š
        "\x8b": "\u2039",  # ‹
        "\x8c": "\u0152",  # Œ
        "\x8e": "\u017d",  # Ž
        "\x91": "\u2018",  # '
        "\x92": "\u2019",  # '
        "\x93": "\u201c",  # "
        "\x94": "\u201d",  # "
        "\x95": "\u2022",  # •
        "\x96": "\u2013",  # –
        "\x97": "\u2014",  # —
        "\x98": "\u02dc",  # ˜
        "\x99": "\u2122",  # ™
        "\x9a": "\u0161",  # š
        "\x9b": "\u203a",  # ›
        "\x9c": "\u0153",  # œ
        "\x9e": "\u017e",  # ž
        "\x9f": "\u0178",  # Ÿ
    }
    for old_char, new_char in CP1252_MAP.items():
        html_fragment = html_fragment.replace(old_char, new_char)

    # Remove &nbsp; → space (already handled by unescape → \xa0)
    html_fragment = html_fragment.replace("\xa0", " ")

    # Clean up whitespace
    # Replace multiple spaces with single space (but preserve newlines for structure)
    html_fragment = re.sub(r"[ \t]+", " ", html_fragment)
    # Replace multiple newlines with single newline
    html_fragment = re.sub(r"\n\s*\n", "\n", html_fragment)
    # Remove leading/trailing whitespace on each line
    lines = [line.strip() for line in html_fragment.split("\n")]
    html_fragment = "\n".join(line for line in lines if line)

    # Remove empty tags
    html_fragment = re.sub(r"<p>\s*</p>", "", html_fragment)
    html_fragment = re.sub(r"<b>\s*</b>", "", html_fragment)
    html_fragment = re.sub(r"<i>\s*</i>", "", html_fragment)
    html_fragment = re.sub(r"<em>\s*</em>", "", html_fragment)
    html_fragment = re.sub(r"<strong>\s*</strong>", "", html_fragment)
    html_fragment = re.sub(r"<li>\s*</li>", "", html_fragment)
    html_fragment = re.sub(r"<td>\s*</td>", "", html_fragment)
    html_fragment = re.sub(r"<tr>\s*</tr>", "", html_fragment)
    html_fragment = re.sub(r"<table>\s*</table>", "", html_fragment)

    # Clean up again after removals
    html_fragment = re.sub(r"\n\s*\n", "\n", html_fragment)

    return html_fragment.strip()


def process_file(source_file_rel):
    """Process a single .htm file and return clean HTML content."""
    filepath = os.path.join(BASE_DIR, source_file_rel)

    if not os.path.exists(filepath):
        return None, f"File not found: {filepath}"

    raw_html = read_file(filepath)
    content = extract_body_content(raw_html)
    clean = clean_html_fragment(content)

    return clean, None


def process_json(input_file, output_file, content_key="html"):
    """Process a JSON file of items, re-extracting HTML from source files."""
    input_path = os.path.join(DATA_DIR, input_file)
    output_path = os.path.join(DATA_DIR, output_file)

    with open(input_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    results = []
    errors = []

    for i, item in enumerate(items):
        source = item["source_file"]
        html_content, error = process_file(source)

        if error:
            errors.append(f"[{i}] {error}")
            html_content = ""

        result = {
            "date": item["date"],
            "title": item["title"],
            "html": html_content,
            "source_file": item["source_file"],
        }

        # Preserve extra keys (like 'section' in paginas)
        for key in item:
            if key not in ("date", "title", "text", "source_file"):
                result[key] = item[key]

        results.append(result)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return len(results), errors


def main():
    print("=== Processing comunicados ===")
    count_c, errors_c = process_json(
        "quercus_comunicados.json", "quercus_comunicados_html.json"
    )
    print(f"Processed: {count_c} comunicados")
    if errors_c:
        print(f"Errors ({len(errors_c)}):")
        for e in errors_c:
            print(f"  {e}")

    print()
    print("=== Processing paginas ===")
    count_p, errors_p = process_json(
        "quercus_paginas.json", "quercus_paginas_html.json"
    )
    print(f"Processed: {count_p} paginas")
    if errors_p:
        print(f"Errors ({len(errors_p)}):")
        for e in errors_p:
            print(f"  {e}")

    print()
    print(f"Total: {count_c} comunicados + {count_p} paginas = {count_c + count_p}")
    print(f"Total errors: {len(errors_c) + len(errors_p)}")


if __name__ == "__main__":
    main()
