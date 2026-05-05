"""Extract text from a single Word file. Called as subprocess."""
import sys
import os
import time
import json

def main():
    filepath = sys.argv[1]
    abs_path = os.path.abspath(filepath)

    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    time.sleep(1)

    try:
        doc = word.Documents.Open(abs_path, ReadOnly=True,
                                   ConfirmConversions=False,
                                   AddToRecentFiles=False)
        text = doc.Content.Text
        doc.Close(False)
        # Output as JSON to stdout
        print(json.dumps({"ok": True, "text": text}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
    finally:
        try:
            word.Quit()
        except:
            pass

if __name__ == "__main__":
    main()
