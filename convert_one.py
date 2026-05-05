"""Convert .doc to PDF - try without OpenAndRepair. Usage: python convert_one.py <src> <dst>"""
import win32com.client
import sys
import time
import pythoncom
import shutil
import os
import tempfile

src = sys.argv[1]
dst = sys.argv[2]

pythoncom.CoInitialize()

# Copy to temp
temp_dir = tempfile.mkdtemp()
temp_src = os.path.join(temp_dir, os.path.basename(src))
try:
    shutil.copy2(src, temp_src)
except OSError:
    with open(src, 'rb') as fin:
        with open(temp_src, 'wb') as fout:
            fout.write(fin.read())

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
word.AutomationSecurity = 3
time.sleep(2)

doc = None
try:
    doc = word.Documents.Open(temp_src, ReadOnly=True)
    time.sleep(8)

    # Check Word still alive
    try:
        cnt = word.Documents.Count
        print(f"Documents open: {cnt}")
    except:
        print("Word died during open")
        raise

    doc.SaveAs(dst, FileFormat=17)
    time.sleep(2)
    doc.Close(0)
    doc = None
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
    if doc:
        try: doc.Close(0)
        except: pass
finally:
    try: word.Quit()
    except: pass
    try: os.unlink(temp_src)
    except: pass
    try: os.rmdir(temp_dir)
    except: pass
