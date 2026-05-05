"""
Copia imagens seleccionadas do OneDrive para img/activismo/ no repo.
Uso: python copy_images.py
"""

import shutil
from pathlib import Path

ONEDRIVE = Path(r"C:\Users\quent\OneDrive\Arquivo\Ambiente")
DEST = Path(r"C:\Users\quent\Downloads\Claude\CV\img\activismo")

IMAGES = {
    "parque-cidade": [
        ("Parque Cidade/Imagens/logo joana.png", "logo.png"),
        ("Parque Cidade/Imagens/foto aerea grande.jpg", "vista-aerea.jpg"),
        ("Parque Cidade/Imagens/parque aerea limites.jpg", "limites.jpg"),
        ("Parque Cidade/Imagens/mapa construcoes.jpg", "mapa-construcoes.jpg"),
        ("Parque Cidade/Sitio/fotos/aldoar1.jpg", "aldoar.jpg"),
        ("Parque Cidade/Imagens/cartoon.jpg", "cartoon.jpg"),
    ],
    "quercus": [
        ("Quercus/Expediente/Simbolos/Logo verde.jpg", "logo.jpg"),
        (
            "Quercus/Projectos/Conferencia Globalizacao/Cartaz globalizacao.jpg",
            "cartaz-globalizacao.jpg",
        ),
        (
            "Quercus/Grupos de Trabalho/Mindelo/Secretaria/Denuncia estrada na ROM - mapa.jpg",
            "mapa-mindelo.jpg",
        ),
        ("Quercus/Grupos de Trabalho/Porto satelite.jpg", "porto-satelite.jpg"),
        ("Quercus/Marketing/Veados capa.png", "veados.png"),
    ],
}

for folder, files in IMAGES.items():
    dest_dir = DEST / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src_rel, dest_name in files:
        src = ONEDRIVE / src_rel
        dst = dest_dir / dest_name
        if not src.exists():
            print(f"  [ERRO] Nao encontrado: {src}")
            continue
        shutil.copy2(src, dst)
        print(f"  [OK] {dest_name}")

print(f"\nCopiadas {sum(len(f) for f in IMAGES.values())} imagens para {DEST}")
