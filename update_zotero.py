"""
Script para actualizar metadados em falta na base de dados Zotero.
Executa operações sobre zotero.sqlite.
IMPORTANTE: Zotero deve estar FECHADO ao executar este script.
"""

import sqlite3

DB_PATH = r"C:\Users\quent\Zotero\zotero.sqlite"

# Field IDs (from Zotero schema)
FIELD = {
    "title": 1,
    "abstractNote": 2,
    "date": 6,
    "DOI": 8,
    "url": 10,
    "volume": 22,
    "publisher": 25,
    "place": 26,
    "ISBN": 28,
    "pages": 35,
    "publicationTitle": 41,
    "bookTitle": 53,
    "issue": 67,
    "journalAbbreviation": 85,
    "institution": 90,
    "thesisType": 120,
    "university": 121,
    "conferenceName": 68,
}

# Item type IDs
ITEM_TYPE = {
    "book": 7,
    "bookSection": 8,
    "conferencePaper": 11,
    "journalArticle": 22,
    "report": 34,
    "thesis": 37,
}

# Creator type IDs
CREATOR_TYPE = {"contributor": 2, "author": 10, "editor": 12}


def get_or_create_value(cur, value):
    """Get valueID for a string, creating it if it doesn't exist."""
    cur.execute("SELECT valueID FROM itemDataValues WHERE value = ?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO itemDataValues (value) VALUES (?)", (value,))
    return cur.lastrowid


def set_field(cur, item_id, field_name, value):
    """Set a field value for an item. Creates or updates."""
    field_id = FIELD[field_name]
    value_id = get_or_create_value(cur, value)
    cur.execute(
        "SELECT * FROM itemData WHERE itemID = ? AND fieldID = ?", (item_id, field_id)
    )
    if cur.fetchone():
        cur.execute(
            "UPDATE itemData SET valueID = ? WHERE itemID = ? AND fieldID = ?",
            (value_id, item_id, field_id),
        )
        print(
            f"  [UPDATE] {field_name} = {value[:80]}..."
            if len(value) > 80
            else f"  [UPDATE] {field_name} = {value}"
        )
    else:
        cur.execute(
            "INSERT INTO itemData (itemID, fieldID, valueID) VALUES (?, ?, ?)",
            (item_id, field_id, value_id),
        )
        print(
            f"  [ADD] {field_name} = {value[:80]}..."
            if len(value) > 80
            else f"  [ADD] {field_name} = {value}"
        )


def change_item_type(cur, item_id, new_type_name):
    """Change the item type."""
    type_id = ITEM_TYPE[new_type_name]
    cur.execute("UPDATE items SET itemTypeID = ? WHERE itemID = ?", (type_id, item_id))
    print(f"  [TYPE] -> {new_type_name}")


def get_or_create_creator(cur, first_name, last_name):
    """Get or create a creator."""
    cur.execute(
        "SELECT creatorID FROM creators WHERE firstName = ? AND lastName = ?",
        (first_name, last_name),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO creators (firstName, lastName) VALUES (?, ?)",
        (first_name, last_name),
    )
    return cur.lastrowid


def add_creator(
    cur, item_id, first_name, last_name, creator_type="author", order_index=None
):
    """Add a creator to an item if not already present."""
    creator_id = get_or_create_creator(cur, first_name, last_name)
    type_id = CREATOR_TYPE[creator_type]

    # Check if already linked
    cur.execute(
        "SELECT * FROM itemCreators WHERE itemID = ? AND creatorID = ?",
        (item_id, creator_id),
    )
    if cur.fetchone():
        print(f"  [SKIP] Creator {first_name} {last_name} already linked")
        return

    if order_index is None:
        cur.execute(
            "SELECT MAX(orderIndex) FROM itemCreators WHERE itemID = ?", (item_id,)
        )
        max_order = cur.fetchone()[0]
        order_index = (max_order or 0) + 1

    cur.execute(
        "INSERT INTO itemCreators (itemID, creatorID, creatorTypeID, orderIndex) VALUES (?, ?, ?, ?)",
        (item_id, creator_id, type_id, order_index),
    )
    print(f"  [ADD] {creator_type}: {first_name} {last_name} (order={order_index})")


def remove_creator(cur, item_id, first_name, last_name):
    """Remove a creator from an item."""
    cur.execute(
        "SELECT creatorID FROM creators WHERE firstName = ? AND lastName = ?",
        (first_name, last_name),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "DELETE FROM itemCreators WHERE itemID = ? AND creatorID = ?",
            (item_id, row[0]),
        )
        print(f"  [REMOVE] Creator: {first_name} {last_name}")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ========================================================
    # ID 49 - A relação entre conflitos armados...
    # ========================================================
    print("\n=== ID 49: A relação entre conflitos armados... ===")
    set_field(cur, 49, "date", "2003-11")
    set_field(
        cur,
        49,
        "publicationTitle",
        "Relações Internacionais do Ambiente, Mestrado em Gestão e Políticas Ambientais, Universidade de Aveiro",
    )
    set_field(
        cur,
        49,
        "abstractNote",
        "A eclosão ou prolongamento de diversos conflitos armados está directa ou indirectamente "
        "relacionada com a luta pelo controlo de importantes recursos naturais. O presente artigo "
        "revela o ciclo destrutivo que se autoalimenta e é caracterizado pela venda desses recursos "
        "em troca de armas, que por sua vez são usadas no controlo de territórios ainda mais vastos "
        "e aterrorizar as populações locais. Deste processo resultam violações sistemáticas aos "
        "direitos humanos e uma destruição ambiental ruinosa.",
    )

    # ========================================================
    # ID 50 - Plano Estratégico de Ambiente do Grande Porto
    # ========================================================
    print("\n=== ID 50: Plano Estratégico de Ambiente... ===")
    set_field(cur, 50, "date", "2003-11")
    add_creator(cur, 50, "Margarida", "Silva")

    # ========================================================
    # ID 51 - Utilização de mecanismos de mercado (1 autor)
    # ========================================================
    print("\n=== ID 51: Utilização de mecanismos de mercado (1 autor) ===")
    set_field(cur, 51, "date", "2004-02")

    # ========================================================
    # ID 52 - Utilização de mecanismos de mercado (5 autores)
    # ========================================================
    print("\n=== ID 52: Utilização de mecanismos de mercado (5 autores) ===")
    set_field(cur, 52, "date", "2005")
    set_field(
        cur,
        52,
        "title",
        "Utilização de mecanismos de mercado para melhor ordenar o território do Grande Porto",
    )
    add_creator(cur, 52, "Pedro", "Santos")
    add_creator(cur, 52, "Margarida", "Silva")

    # ========================================================
    # ID 53 - O Conceito de Desenvolvimento Sustentável...
    # ========================================================
    print("\n=== ID 53: O Conceito de Desenvolvimento Sustentável... ===")
    set_field(cur, 53, "date", "2005-05")
    set_field(
        cur,
        53,
        "abstractNote",
        "Este trabalho procura oferecer um enquadramento teórico e prático sobre o tema do "
        "Desenvolvimento Sustentável, em particular as questões relacionadas com o "
        "desenvolvimento do território, as cidades sustentáveis e o ambiente urbano. "
        "Pretende-se assim analisar as consequências advindas das várias recomendações/"
        "estratégias emanadas dos vários momentos históricos (conferências e relatórios) "
        "que compõem a evolução deste conceito, no território nacional.",
    )

    # ========================================================
    # ID 54 - Um sistema de governança (versão working paper)
    # ========================================================
    print("\n=== ID 54: Um sistema de governança (working paper) ===")
    set_field(cur, 54, "date", "2006-05")

    # ========================================================
    # ID 55 - Naturbanization and sustainability at Peneda-Gerês
    # CHANGE TYPE: journalArticle -> bookSection
    # ========================================================
    print("\n=== ID 55: Naturbanization (change to bookSection) ===")
    change_item_type(cur, 55, "bookSection")
    set_field(cur, 55, "date", "2009")
    set_field(
        cur,
        55,
        "bookTitle",
        "Naturbanization: New identities and processes for rural-natural areas",
    )
    set_field(cur, 55, "publisher", "Taylor & Francis Group")
    set_field(cur, 55, "place", "London")
    set_field(cur, 55, "ISBN", "978-0-415-49000-9")
    # Add editor: Prados
    add_creator(cur, 55, "María José", "Prados", creator_type="editor")

    # ========================================================
    # ID 56 - How can the stigma of public transport...
    # Only missing abstract
    # ========================================================
    print("\n=== ID 56: Stigma of public transport (abstract) ===")
    set_field(
        cur,
        56,
        "abstractNote",
        "Natural Resources Forum special series on themes considered by the United Nations "
        "Commission on Sustainable Development. In this issue, experts address the question: "
        "\"How can the stigma of public transport as the 'poor man's vehicle' be overcome "
        'to enhance sustainability and climate change mitigation?" A collection of viewpoints '
        "from international experts on transport policy, sustainability, and urban planning.",
    )

    # ========================================================
    # ID 57 - Sustainability: characteristics and scientific roots
    # Only missing abstract
    # ========================================================
    print("\n=== ID 57: Sustainability characteristics (abstract) ===")
    set_field(
        cur,
        57,
        "abstractNote",
        "Literature about sustainable development is abundant and expanding, and syntheses are "
        "therefore increasingly necessary. This paper represents an effort to characterize the main "
        "principles behind the concept of sustainability and to identify and describe the scientific "
        "approaches at the root of each of those principles. From a scientific point of view, the "
        "identification of sustainability principles is possibly more interesting than providing one "
        "rigid definition because they are more abstract and conceptual. As a first step, three "
        "scientific approaches relevant in the context of sustainability—ecological economics, "
        "sustainability transition, and sustainability science—were characterized and synthesized "
        "into four sustainability principles. The next step was the identification and description of "
        "the scientific approaches at the root of each sustainability principle. Four sustainability "
        "principles were identified: the stressing of biophysical limits that constrain the scale of "
        "the human economy; the focus on societal welfare and development; the understanding that "
        "each system has its own minimum irreducible needs in order to be viable; and the "
        "acknowledgment of system complexity.",
    )

    # ========================================================
    # ID 76 - Células de combustível (report, already has date)
    # ========================================================
    print("\n=== ID 76: Células de combustível ===")
    # Already has date 2003-10-06, just confirm type is report
    # It's already a report, nothing critical to add

    # ========================================================
    # ID 77 - Um sistema de governança (Eixo Atlântico)
    # Already has date, journal, volume, pages
    # ========================================================
    print("\n=== ID 77: Governança GAMP (Eixo Atlântico) ===")
    # Already reasonably complete

    # ========================================================
    # ID 78 - Ordenar melhor o território (Impactus)
    # ========================================================
    print("\n=== ID 78: Impactus ===")
    set_field(cur, 78, "pages", "50-51")

    # ========================================================
    # ID 79 - Modeling a sustainable urban structure (PhD thesis)
    # ========================================================
    print("\n=== ID 79: PhD thesis ===")
    # Already has most metadata, just confirm it's complete

    # ========================================================
    # ID 81 - A spectral study of nutrient and disease stress
    # CHANGE TYPE: report -> thesis
    # ========================================================
    print("\n=== ID 81: Spectral study (change to thesis) ===")
    change_item_type(cur, 81, "thesis")
    set_field(cur, 81, "date", "2001")
    set_field(cur, 81, "university", "Katholieke Universiteit Leuven")
    set_field(cur, 81, "thesisType", "Master Thesis")
    set_field(cur, 81, "place", "Leuven")

    # ========================================================
    # ID 91 - Indicadores de desenvolvimento sustentável
    # CHANGE TYPE: journalArticle -> report
    # ========================================================
    print("\n=== ID 91: Indicadores de DS (change to report) ===")
    change_item_type(cur, 91, "report")
    set_field(cur, 91, "date", "2006-01")
    set_field(
        cur,
        91,
        "institution",
        "Futuro Sustentável / Escola Superior de Biotecnologia, Universidade Católica Portuguesa",
    )
    set_field(cur, 91, "place", "Porto")
    # Add authors
    add_creator(cur, 91, "Nuno", "Quental", order_index=0)
    add_creator(cur, 91, "Pedro", "Macedo", order_index=1)
    add_creator(cur, 91, "Margarida", "Silva", order_index=2)
    set_field(
        cur,
        91,
        "abstractNote",
        "Compilação de indicadores de desenvolvimento sustentável para a região do Grande Porto. "
        "Os indicadores estão organizados segundo uma tipologia composta por diversos domínios, "
        "enquadrados na metodologia da Agência Europeia do Ambiente denominada DPSIR "
        "(Forças motrizes, pressões, estado, impactes e respostas). Os dados foram trabalhados "
        "para revelar diferenças entre municípios, evoluções temporais e relações com outros indicadores.",
    )

    # ========================================================
    # ID 92 - Integração de critérios objectivos...
    # CHANGE TYPE: journalArticle -> conferencePaper
    # ========================================================
    print("\n=== ID 92: Critérios objectivos (change to conferencePaper) ===")
    change_item_type(cur, 92, "conferencePaper")
    set_field(
        cur,
        92,
        "conferenceName",
        "XI Jornadas da AUP - Território e Desenvolvimento: os Argumentos e a Disciplina do Urbanismo",
    )
    set_field(cur, 92, "date", "2004")
    # Add missing 3rd author: Júlia Lourenço
    add_creator(cur, 92, "Júlia", "Lourenço")

    # ========================================================
    # ID 93 - Diagnóstico e Plano de Acção
    # Fix title, fix author, add date
    # CHANGE TYPE: journalArticle -> report
    # ========================================================
    print("\n=== ID 93: Diagnóstico e Plano de Acção ===")
    change_item_type(cur, 93, "report")
    set_field(
        cur, 93, "title", "Espaços verdes e rio Ul — Diagnóstico e Plano de Acção"
    )
    set_field(cur, 93, "date", "2004-05")
    set_field(cur, 93, "place", "São João da Madeira")
    set_field(
        cur,
        93,
        "institution",
        "Agenda 21 Local de São João da Madeira / Escola Superior de Biotecnologia, UCP",
    )
    # Remove wrong author "Maio de" and add correct one
    remove_creator(cur, 93, "Maio", "de")
    add_creator(cur, 93, "Nuno", "Quental", order_index=0)

    # ========================================================
    # ID 94 - Definição de uma estrutura ecológica...
    # CHANGE TYPE: journalArticle -> conferencePaper
    # ========================================================
    print("\n=== ID 94: Estrutura ecológica SJM (change to conferencePaper) ===")
    change_item_type(cur, 94, "conferencePaper")
    set_field(cur, 94, "date", "2004")
    set_field(
        cur,
        94,
        "abstractNote",
        "O Decreto-Lei n.º 380/99, com as alterações introduzidas pelo Decreto-Lei n.º 310/2003, "
        "que desenvolve as bases da política de ordenamento do território, impõe, no seu artigo 85.º, "
        'alínea c), "a definição dos sistemas de protecção dos valores e recursos naturais, culturais, '
        'agrícolas e florestais, identificando a estrutura ecológica municipal" em sede de Plano '
        "Director Municipal (PDM). No âmbito da Agenda 21 Local de São João da Madeira foram "
        "seleccionados por processos participativos oito temas prioritários para análise. Entre eles "
        'figuram os "espaços verdes e rio Antuã". Optou-se por definir uma estrutura ecológica para '
        "o município, satisfazendo as aspirações dos cidadãos no que respeita à dotação de espaços "
        "verdes e relativamente a outras queixas relacionadas com os espaços naturais existentes.",
    )

    # ========================================================
    # Correcção de acentos em falta
    # ========================================================
    accent_fixes = {
        182: (
            "Centro Historico do Porto numa encruzilhada",
            "Centro Histórico do Porto numa encruzilhada",
        ),
        168: (
            "O plátano de Damião de Góis e a politica na cidade",
            "O plátano de Damião de Góis e a política na cidade",
        ),
        170: ("Quando o exemplo nao vem de cima", "Quando o exemplo não vem de cima"),
        267: (
            "Uma catastrofe ambiental as portas de Portugal, a mare negra do Prestige",
            "Uma catástrofe ambiental às portas de Portugal, a maré negra do Prestige",
        ),
        206: ("Que e feito do litoral português", "Que é feito do litoral português"),
        186: ("Haia mudara o clima?", "Haia mudará o clima?"),
    }
    print("\n=== Correcção de acentos em títulos ===")
    for item_id, (old_title, new_title) in accent_fixes.items():
        set_field(cur, item_id, "title", new_title)

    conn.commit()
    print("\n✓ Base de dados actualizada com sucesso!")
    print("  Backup em: C:\\Users\\quent\\Zotero\\zotero.sqlite.backup_claude_*")
    conn.close()


if __name__ == "__main__":
    main()
