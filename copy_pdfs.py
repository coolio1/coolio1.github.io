import shutil
import os

dest = r"C:\Users\quent\Downloads\Claude\CV\pdfs\Voluntariado"

shutil.copy2(
    r"C:\Users\quent\OneDrive\Arquivo\Ambiente\UOPG1 - Nun Alvares\2025\2025-07-20 - PDA Nun Alvares.pdf",
    os.path.join(dest, "2025-07-20 - PDA Nun Alvares.pdf"),
)
print("OK")
