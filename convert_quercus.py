"""Convert all Quercus .doc files to PDF using Word COM automation.
Disables File Block settings temporarily, restarts Word if COM connection drops."""
import win32com.client
import os
import time
import subprocess
import winreg

SRC_ROOT = r"C:\Users\quent\OneDrive\Arquivo\Ambiente\Quercus"
DST_ROOT = r"C:\Users\quent\Downloads\Claude\CV\pdfs\Voluntariado\Quercus"

EXCLUDE_BASENAMES = {
    "Cont_Int_Quercus2.doc",  # contact list
}

def disable_file_block():
    """Disable Word File Block settings in the registry to allow opening old .doc files."""
    # Word 2016/365 uses version 16.0
    key_path = r"Software\Microsoft\Office\16.0\Word\Security\FileBlock"
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        # Set all FileBlock entries to 0 (don't block)
        for i in range(1, 17):
            name = f"Word{i}Files" if i <= 12 else f"Word{i}Files"
            try:
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, 0)
            except:
                pass
        # Also set these specific ones
        for name in ["Word2Files", "Word6Files", "Word97Files", "Word60Files",
                     "Word95Files", "FilesBeforeVersion", "OpenInProtectedView"]:
            try:
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, 0)
            except:
                pass
        winreg.CloseKey(key)
        print("File Block settings disabled in registry.")
    except Exception as e:
        print(f"Warning: Could not modify registry: {e}")

def collect_docs(root):
    docs = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.lower().endswith(".doc") and not f.lower().endswith(".docx"):
                full = os.path.join(dirpath, f)
                docs.append(full)
    return sorted(docs)

def src_to_dst(src_path):
    rel = os.path.relpath(src_path, SRC_ROOT)
    base, _ = os.path.splitext(rel)
    return os.path.join(DST_ROOT, base + ".pdf")

def kill_word():
    try:
        subprocess.run(["taskkill", "/f", "/im", "WINWORD.EXE"],
                       capture_output=True, timeout=10)
    except:
        pass
    time.sleep(2)

def start_word():
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    return word

def convert_one(word, src, dst):
    doc = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
    doc.SaveAs(dst, FileFormat=17)
    doc.Close(0)
    return word

def is_rpc_error(e):
    """Check if the error is a COM/RPC connection failure."""
    s = str(e)
    return "RPC" in s or "-2147023174" in s or "-2147023170" in s or "-2147418111" in s

def main():
    disable_file_block()

    docs = collect_docs(SRC_ROOT)
    docs = [d for d in docs if os.path.basename(d) not in EXCLUDE_BASENAMES]
    print(f"Found {len(docs)} .doc files to convert")

    kill_word()
    word = start_word()

    converted = []
    errors = []
    skipped = []

    for i, src in enumerate(docs, 1):
        dst = src_to_dst(src)
        dst_dir = os.path.dirname(dst)
        os.makedirs(dst_dir, exist_ok=True)

        if os.path.exists(dst):
            skipped.append(src)
            print(f"[{i}/{len(docs)}] SKIP (exists): {os.path.basename(src)}")
            continue

        rel = os.path.relpath(src, SRC_ROOT)
        print(f"[{i}/{len(docs)}] Converting: {rel}", flush=True)

        try:
            word = convert_one(word, src, dst)
            converted.append(src)
            print(f"  OK -> {os.path.basename(dst)}", flush=True)
        except Exception as e:
            if is_rpc_error(e):
                print(f"  COM error, restarting Word...", flush=True)
                kill_word()
                try:
                    word = start_word()
                    word = convert_one(word, src, dst)
                    converted.append(src)
                    print(f"  OK (after restart) -> {os.path.basename(dst)}", flush=True)
                except Exception as e2:
                    errors.append((src, str(e2)))
                    print(f"  FAILED: {e2}", flush=True)
                    kill_word()
                    try:
                        word = start_word()
                    except:
                        pass
            else:
                # Non-RPC error (e.g. Trust Center, corrupt file) -- just log and continue
                errors.append((src, str(e)))
                print(f"  FAILED: {e}", flush=True)

    try:
        word.Quit()
    except:
        kill_word()

    print(f"\n=== SUMMARY ===")
    print(f"Converted: {len(converted)}")
    print(f"Skipped (already exist): {len(skipped)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nFailed files:")
        for src, err in errors:
            print(f"  {os.path.relpath(src, SRC_ROOT)}: {err}")

    if converted:
        print("\nConverted files:")
        for src in converted:
            print(f"  {os.path.relpath(src, SRC_ROOT)}")

if __name__ == "__main__":
    main()
