# Regras do projecto CV

## Sobre o projecto
Site estático (Jekyll / GitHub Pages) com CV, escritos e activismo do Nuno Quental.
Publicado em **coolio1.github.io** (repo `coolio1/coolio1.github.io`).
Scripts Python geram as páginas HTML a partir de dados do Zotero e PDFs locais.

## Stack
- **Site:** Jekyll (HTML + CSS estático, `_config.yml`)
- **Geração:** Python (`generate_site.py`, `generate_activismo_*.py`, `update_zotero.py`)
- **Fonte de dados:** Zotero (`C:\Users\quent\Zotero\export.json` — exportado da BD SQLite)
- **PDFs:** `pdfs/` (documentos), links apontam para `C:\Users\quent\OneDrive\Documentos\Escritos (versoes finais)`
- **Imagens:** `img/`, `logos/`, `covers/`

## Estrutura do projecto

```
CV/
├── _config.yml                    # Configuração Jekyll (com exclude para *.py, data/, etc.)
├── .nojekyll                      # Desactiva processamento Jekyll (GitHub Pages serve estático)
├── .gitignore                     # Ignora __pycache__, .claude/, .superpowers/, *.bak, .env
├── requirements.txt               # Dependências Python (pywin32)
├── index.html                     # Página principal (CV)
├── escritos.html                  # Página de escritos/publicações
├── activismo*.html                # Páginas de activismo (geradas)
├── site_data.py                   # Funções puras partilhadas: load_items, categorize,
│                                  #   format_apa, render_items, render_featured, etc.
│                                  #   Importado por generate_site.py e outros geradores
├── generate_site.py               # Gerador principal → index.html, escritos.html
│                                  #   Lê: C:\Users\quent\Zotero\export.json via site_data
│                                  #   Escreve: index.html, escritos.html
├── generate_activismo_parque.py   # Gerador → activismo-parque.html
├── generate_activismo_quercus.py  # Gerador → activismo-quercus.html
├── update_zotero.py               # Acede directamente a zotero.sqlite (Zotero DEVE estar fechado)
├── convert_one.py                 # Conversão doc→PDF individual (Word COM)
├── convert_parque.py              # Conversão documentos Parque da Cidade
├── convert_quercus.py             # Conversão documentos Quercus
├── copy_images.py                 # Copiar imagens de capas
├── copy_pdfs.py                   # Copiar PDFs para pasta local
├── extract_texts.py               # Extracção de texto de PDFs (chama extract_single.py)
├── extract_single.py              # Helper de extracção (subprocess)
├── data/                          # Textos extraídos (JSON)
├── pdfs/                          # Documentos originais (PDF)
│   └── activismo/                 # PDFs de activismo
├── img/                           # Capas de publicações (JPG)
├── logos/                         # Logos de organizações
└── covers/                        # Capas adicionais
```

## Workflow de publicação

1. **Actualizar Zotero** — adicionar/editar publicações no Zotero desktop
2. **Exportar** — `File → Export Library → Better CSL JSON` → `C:\Users\quent\Zotero\export.json`
   (ou correr `update_zotero.py` com Zotero fechado para acesso directo à BD)
3. **Regenerar** — `python generate_site.py` (e scripts de activismo se necessário)
4. **Verificar** — abrir HTML localmente, confirmar links e formatação
5. **Publicar** — `git add . && git commit && git push` → GitHub Pages actualiza automaticamente

## Dependências externas

- **Zotero** → `export.json` é a fonte autoritativa de publicações
- **OneDrive** → PDFs originais em `Documentos\Escritos (versoes finais)` (read-only, nunca modificar)
- **Porto Verde** → site irmão em `coolio1/porto_areas_verdes_mudanca` (mesmo utilizador GitHub)

## Validação
- Após alterar scripts de geração, correr o script e verificar que o HTML resultante está correcto
- Links relativos entre páginas devem funcionar (testar com `python -m http.server` se necessário)

## Higiene do repositório

- Regras base (`.gitignore`, scripts one-off, binários grandes): ver global.
- **`_config.yml` exclude** — mesmo com `.nojekyll`, manter secção `exclude` como defesa em profundidade.
- **`requirements.txt`** — manter actualizado ao adicionar dependências.

## Lições aprendidas
- PDFs do OneDrive são read-only — copiar para `pdfs/` antes de processar
- `generate_site.py` tem overrides manuais de datas para 4 itens do Zotero que não têm data no export
- Ordem de publicações: sempre cronológica inversa (mais recente primeiro)
- Scripts `convert_*_retry*.py` e `debug_word.py` foram removidos (2026-04) — eram one-off já executados

## Jekyll — comandos essenciais

Ver skill `/jekyll`. Config específica deste site: `baseurl` vazio (repo principal `coolio1.github.io`); `generate_site.py` consome `C:\Users\quent\Zotero\export.json`.
