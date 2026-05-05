"""Extract text from Word and PDF documents for CV site embedding."""

import json
import os
import re
import time

# ── Helpers ──────────────────────────────────────────────────────────

def clean_text(text):
    """Clean extracted text: fix encoding, normalise whitespace, preserve paragraphs."""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace('\x07', '').replace('\x0b', '\n').replace('\x0c', '\n')
    text = text.replace('\xa0', ' ')
    text = text.replace('\u2013', '\u2013').replace('\u2014', '\u2014')
    # Normalise line breaks: 2+ newlines -> paragraph break
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse runs of spaces/tabs on same line
    text = re.sub(r'[^\S\n]+', ' ', text)
    # Strip leading/trailing whitespace per line
    lines = [l.strip() for l in text.split('\n')]
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class WordExtractor:
    """Manages Word COM with auto-restart on crash."""

    def __init__(self):
        self.word = None
        self._start()

    def _start(self):
        import win32com.client
        try:
            if self.word:
                try:
                    self.word.Quit()
                except:
                    pass
        except:
            pass
        time.sleep(2)
        # Kill any lingering Word processes
        os.system('taskkill /f /im WINWORD.EXE >nul 2>&1')
        time.sleep(2)
        self.word = win32com.client.Dispatch("Word.Application")
        self.word.Visible = False
        self.word.DisplayAlerts = 0  # wdAlertsNone
        time.sleep(1)

    def extract(self, filepath, retries=2):
        abs_path = os.path.abspath(filepath)
        fname = os.path.basename(abs_path)
        for attempt in range(retries):
            if attempt > 0:
                print(f"  Retry {attempt} for: {fname}")
            else:
                print(f"  Opening: {fname}")
            try:
                doc = self.word.Documents.Open(abs_path, ReadOnly=True,
                                                ConfirmConversions=False,
                                                AddToRecentFiles=False)
                text = doc.Content.Text
                doc.Close(False)
                time.sleep(0.5)
                return clean_text(text)
            except Exception as e:
                print(f"  ERROR: {fname}: {e}")
                try:
                    print("  Restarting Word...")
                    self._start()
                    print("  Word restarted.")
                except Exception as e2:
                    print(f"  Failed to restart Word: {e2}")
        return None

    def quit(self):
        try:
            self.word.Quit()
        except:
            pass


def extract_pdf(filepath):
    """Extract text from PDF via PyMuPDF."""
    import fitz
    abs_path = os.path.abspath(filepath)
    print(f"  Opening PDF: {os.path.basename(abs_path)}")
    doc = fitz.open(abs_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return clean_text('\n\n'.join(pages))


def save_json(data, output_path):
    """Save list of dicts as JSON."""
    data.sort(key=lambda x: x.get('date', ''))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {len(data)} entries to {os.path.basename(output_path)}")


# ── Paths ────────────────────────────────────────────────────────────

BASE = r"C:\Users\quent\OneDrive\Arquivo\Ambiente"
OUT = r"C:\Users\quent\Downloads\Claude\CV\data"

# ── Main ─────────────────────────────────────────────────────────────

def main():
    wx = WordExtractor()
    totals = {}

    try:
        # ── 1. MUT ───────────────────────────────────────────────────
        print("\n=== MUT ===")
        mut = []
        mut_dir = os.path.join(BASE, "MUT")
        mut_files = [
            ("2006-03-16", "Convocatoria MUT", "2006-03-16 - Convocatoria MUT.doc"),
            ("2006-03-17", "Comunicado MUT", "2006-03-17 - Comunicado MUT.doc"),
            ("2006-06-02", "Cartaz MUT", "2006-06-02 - Cartaz.doc"),
            ("2007-01-12", "STCP, do servico publico a falta de servico", "2007-01-12 - STCP, do servico publico a falta de servico.doc"),
            ("2007-01-30", "Carta plenario STCP", "2007-01-30 - Carta plenario STCP.doc"),
            ("2006", "Acta n.o 2 do MUTP", "MUTP Acta nr 2.doc"),
        ]
        for date, title, fname in mut_files:
            fpath = os.path.join(mut_dir, fname)
            if os.path.exists(fpath):
                text = wx.extract(fpath)
                if text is not None:
                    mut.append({"date": date, "title": title, "text": text, "source_file": fname})
            else:
                print(f"  NOT FOUND: {fname}")
        save_json(mut, os.path.join(OUT, "mut_textos.json"))
        totals["mut_textos.json"] = len(mut)

        # ── 2. Jardim do Marques ─────────────────────────────────────
        print("\n=== Jardim do Marques ===")
        marques = []
        marques_dir = os.path.join(BASE, "Marques")
        marques_files = [
            ("", "Abaixo-assinado Jardim do Marques", "Abaixo-assinado marques.doc"),
            ("", "Comunicado manifestacao Jardim do Marques", "comunicado manif.doc"),
            ("", "Folheto Jardim do Marques", "folheto.DOC"),
            ("", "Folheto 2 Jardim do Marques", "folheto2.doc"),
        ]
        for date, title, fname in marques_files:
            fpath = os.path.join(marques_dir, fname)
            if os.path.exists(fpath):
                text = wx.extract(fpath)
                if text is not None:
                    marques.append({"date": date, "title": title, "text": text, "source_file": fname})
            else:
                print(f"  NOT FOUND: {fname}")
        save_json(marques, os.path.join(OUT, "marques_textos.json"))
        totals["marques_textos.json"] = len(marques)

        # ── 3. GARRA ────────────────────────────────────────────────
        print("\n=== GARRA ===")
        garra = []
        garra_dir = os.path.join(BASE, "GARRA")
        # Find .docx file dynamically (filename has accented chars)
        garra_docx = [f for f in os.listdir(garra_dir) if f.endswith('.docx')]
        if garra_docx:
            garra_fname = garra_docx[0]
            fpath = os.path.join(garra_dir, garra_fname)
            text = wx.extract(fpath)
            if text is not None:
                garra.append({
                    "date": "",
                    "title": "Carta aberta ao Presidente da Camara do Porto - Ramal da Alfandega",
                    "text": text,
                    "source_file": garra_fname
                })
        else:
            print("  WARNING: GARRA docx not found")
        save_json(garra, os.path.join(OUT, "garra_textos.json"))
        totals["garra_textos.json"] = len(garra)

        # ── 4. Farol-Terra ──────────────────────────────────────────
        print("\n=== Farol-Terra ===")
        farol = []
        farol_dir = os.path.join(BASE, "Farol")
        farol_files = [
            ("", "Transgenicos - comunicado de imprensa", "Transgenicos - imprensa.doc"),
            ("", "Comunicado eleicoes AEESB", "Comunicado eleicoes AEESB.doc"),
            ("", "Congresso GOSEA", "Congresso GOSEA.doc"),
        ]
        for date, title, fname in farol_files:
            fpath = os.path.join(farol_dir, fname)
            if os.path.exists(fpath):
                text = wx.extract(fpath)
                if text is not None:
                    farol.append({"date": date, "title": title, "text": text, "source_file": fname})
            else:
                print(f"  NOT FOUND: {fname}")
        save_json(farol, os.path.join(OUT, "farol_textos.json"))
        totals["farol_textos.json"] = len(farol)

        # ── 5. Centro Historico ─────────────────────────────────────
        print("\n=== Centro Historico ===")
        centro = []
        ch_dir = os.path.join(BASE, "Centro Historico do Porto")
        pdf_files = [f for f in os.listdir(ch_dir) if f.endswith('.pdf') and 'fachadismo' in f.lower()]
        if pdf_files:
            pdf_fname = pdf_files[0]
            fpath = os.path.join(ch_dir, pdf_fname)
            text = extract_pdf(fpath)
            centro.append({
                "date": "",
                "title": "Centro Historico do Porto: pela recuperacao, contra o fachadismo",
                "text": text,
                "source_file": pdf_fname
            })
        else:
            print("  WARNING: Petition PDF not found")
        save_json(centro, os.path.join(OUT, "centro_historico_textos.json"))
        totals["centro_historico_textos.json"] = len(centro)

        # ── 6. Outros ───────────────────────────────────────────────
        print("\n=== Outros ===")
        outros = []
        outros_dir = os.path.join(BASE, "Outros")

        # Declaracao
        decl_path = os.path.join(outros_dir, "Declaracao sobre o ambiente e o futuro de Portugal",
                                  "Declaracao sobre o ambiente e o futuro de Portugal.doc")
        if os.path.exists(decl_path):
            text = wx.extract(decl_path)
            if text is not None:
                outros.append({
                    "date": "",
                    "title": "Declaracao sobre o ambiente e o futuro de Portugal",
                    "text": text,
                    "source_file": "Declaracao sobre o ambiente e o futuro de Portugal.doc"
                })

        # PROMindelo
        pro_path = os.path.join(outros_dir, "2009-05-14 - Parecer PROMindelo.pdf")
        if os.path.exists(pro_path):
            text = extract_pdf(pro_path)
            outros.append({
                "date": "2009-05-14",
                "title": "Parecer PROMindelo",
                "text": text,
                "source_file": "2009-05-14 - Parecer PROMindelo.pdf"
            })
        else:
            print("  WARNING: PROMindelo PDF not found")

        # ── 7. Root Ambiente files -> add to outros ──────────────────
        print("\n=== Root Ambiente ===")
        root_files = [
            ("2026-01-16", "Carta ICNF Pinhal de Ovar", "2026-01-16 - Carta ICNF Pinhal de Ovar.docx"),
            ("2026-03-27", "Companhia Aurifica (com Quinta do Pinheiro)", "2026-03-27 - Companhia Aurificia (com Quinta do Pinheiro).docx"),
        ]
        for date, title, fname in root_files:
            fpath = os.path.join(BASE, fname)
            if os.path.exists(fpath):
                text = wx.extract(fpath)
                if text is not None:
                    outros.append({"date": date, "title": title, "text": text, "source_file": fname})
            else:
                print(f"  NOT FOUND: {fname}")

        save_json(outros, os.path.join(OUT, "outros_textos.json"))
        totals["outros_textos.json"] = len(outros)

    finally:
        wx.quit()
        print("\nWord closed.")

    # ── Report ───────────────────────────────────────────────────────
    print("\n=== TOTALS ===")
    grand = 0
    for fname, count in totals.items():
        print(f"  {fname}: {count} entries")
        grand += count
    print(f"  TOTAL: {grand} entries across {len(totals)} files")


if __name__ == "__main__":
    main()
