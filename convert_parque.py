"""Convert all .doc files from Parque Cidade to PDF - one Word per file."""
import win32com.client
import os
import shutil
import time
import pythoncom
import tempfile
import subprocess

src_comunicados = r'C:\Users\quent\OneDrive\Arquivo\Ambiente\Parque Cidade\Comunicados'
src_root = r'C:\Users\quent\OneDrive\Arquivo\Ambiente\Parque Cidade'
dst_dir = r'C:\Users\quent\Downloads\Claude\CV\pdfs\Voluntariado\Parque da Cidade'

os.makedirs(dst_dir, exist_ok=True)

# Collect all files
all_files = []
for f in sorted(os.listdir(src_comunicados)):
    if f.lower().endswith(('.doc', '.docx')):
        all_files.append((os.path.join(src_comunicados, f), f))

root_relevant = ['Historial do MPC.doc', 'Um negocio mal explicado.doc']
for f in root_relevant:
    src = os.path.join(src_root, f)
    if os.path.exists(src):
        all_files.append((src, f))

print(f"Total files to process: {len(all_files)}\n")

converted = []
copied = []
skipped = []
errors = []

for i, (src_path, filename) in enumerate(all_files, 1):
    base = os.path.splitext(filename)[0]
    pdf_name = base + '.pdf'
    dst = os.path.join(dst_dir, pdf_name)

    print(f"[{i}/{len(all_files)}] {filename}...", end=' ', flush=True)

    if os.path.exists(dst):
        skipped.append(filename)
        print("SKIP")
        continue

    # Check if PDF exists in source
    src_dir_path = os.path.dirname(src_path)
    src_pdf = os.path.join(src_dir_path, pdf_name)
    if os.path.exists(src_pdf):
        try:
            shutil.copy2(src_pdf, dst)
            copied.append(filename)
            print("COPIED")
            continue
        except OSError:
            try:
                with open(src_pdf, 'rb') as fin:
                    with open(dst, 'wb') as fout:
                        fout.write(fin.read())
                copied.append(filename)
                print("COPIED")
                continue
            except OSError:
                pass

    # Convert using subprocess (isolated Python process per file)
    result = subprocess.run(
        ['python', '-c', f'''
import win32com.client, time, pythoncom, shutil, os, tempfile
pythoncom.CoInitialize()

src = r"{src_path}"
dst = r"{dst}"

temp_dir = tempfile.mkdtemp()
temp_src = os.path.join(temp_dir, os.path.basename(src))
try:
    shutil.copy2(src, temp_src)
except OSError:
    with open(src, "rb") as fin:
        with open(temp_src, "wb") as fout:
            fout.write(fin.read())

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
word.AutomationSecurity = 3
time.sleep(2)
doc = word.Documents.Open(temp_src, ConfirmConversions=False, ReadOnly=True, AddToRecentFiles=False, Revert=True, OpenAndRepair=True)
time.sleep(3)
doc.SaveAs(dst, FileFormat=17)
time.sleep(1)
doc.Close(0)
word.Quit()
os.unlink(temp_src)
os.rmdir(temp_dir)
print("OK")
'''],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode == 0 and 'OK' in result.stdout:
        converted.append(filename)
        print("CONVERTED")
    else:
        err_msg = result.stderr.strip().split('\n')[-1] if result.stderr else result.stdout.strip()
        errors.append(f'{filename}: {err_msg}')
        print("ERROR")
        # Clean up bad PDF
        if os.path.exists(dst) and os.path.getsize(dst) == 0:
            os.unlink(dst)

    # Kill any leftover Word
    subprocess.run(['taskkill', '/F', '/IM', 'WINWORD.EXE'], capture_output=True, timeout=10)
    time.sleep(5)

print(f"\n{'='*60}")
print(f"Converted ({len(converted)}):")
for f in converted:
    print(f'  {f}')
print(f"Copied existing PDF ({len(copied)}):")
for f in copied:
    print(f'  {f}')
print(f"Skipped ({len(skipped)}):")
for f in skipped:
    print(f'  {f}')
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f'  {e}')
print(f"\nTotal: {len(converted)} converted, {len(copied)} copied, {len(skipped)} skipped, {len(errors)} errors")
