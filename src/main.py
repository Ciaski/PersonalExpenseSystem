import sqlite3

def inizializza_db():
    conn = sqlite3.connect('Spese_Personali.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Tabella Categorie con vincolo lunghezza nome
    cursor.execute('''CREATE TABLE IF NOT EXISTS categorie (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT UNIQUE NOT NULL CHECK(length(nome) > 0))''')
    
    # Tabella Spese con vincolo importo positivo
    cursor.execute('''CREATE TABLE IF NOT EXISTS spese (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT NOT NULL,
                        importo REAL NOT NULL CHECK(importo > 0),
                        categoria_id INTEGER NOT NULL,
                        descrizione TEXT,
                        FOREIGN KEY (categoria_id) REFERENCES categorie(id))''')
    
    # Tabella Budget con vincoli richiesti
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (
                        mese TEXT NOT NULL, 
                        categoria_id INTEGER NOT NULL, 
                        importo REAL NOT NULL CHECK(importo > 0),
                        PRIMARY KEY (mese, categoria_id),
                        FOREIGN KEY (categoria_id) REFERENCES categorie(id))''')
    conn.commit()
    return conn

def gestione_categorie(conn):
    nome = input("Nome della categoria: ").strip()
    if not nome:
        print("❌ Errore: il nome non può essere vuoto.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("✅ Categoria inserita correttamente.")
    except sqlite3.IntegrityError:
        print("❌ Errore: La categoria esiste già.")

def inserisci_spesa(conn):
    data = input("Data (YYYY-MM-DD): ")
    try:
        importo = float(input("Importo: "))
        if importo <= 0:
            print("❌ Errore: l'importo deve essere maggiore di zero.")
            return
        
        cat_nome = input("Nome della categoria: ")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorie WHERE nome = ?", (cat_nome,))
        risultato = cursor.fetchone()
        
        if risultato:
            cat_id = risultato[0]
            desc = input("Descrizione (facoltativa): ")
            cursor.execute("INSERT INTO spese (data, importo, categoria_id, descrizione) VALUES (?, ?, ?, ?)",
                           (data, importo, cat_id, desc))
            conn.commit()
            print("✅ Spesa inserita correttamente.")
        else:
            print("❌ Errore: la categoria non esiste.")
    except ValueError:
        print("❌ Inserisci un numero valido.")

def definisci_budget(conn):
    mese = input("Mese (YYYY-MM): ")
    cat_nome = input("Nome della categoria: ")
    try:
        importo = float(input("Importo del budget: "))
        if importo <= 0:
            print("❌ Errore: il budget deve essere maggiore di zero.")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorie WHERE nome = ?", (cat_nome,))
        risultato = cursor.fetchone()
        
        if risultato:
            cat_id = risultato[0]
            cursor.execute("INSERT OR REPLACE INTO budget (mese, categoria_id, importo) VALUES (?, ?, ?)",
                           (mese, cat_id, importo))
            conn.commit()
            print("✅ Budget mensile salvato correttamente.")
        else:
            print("❌ Errore: la categoria non esiste.")
    except ValueError:
        print("❌ Inserisci un numero valido.")

def visualizza_report(conn):
    while True:
        print("\n--- MENU REPORT ---")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo spese")
        print("4. Ritorna al menu principale")
        
        scelta = input("Inserisci scelta report: ")
        cursor = conn.cursor()

        if scelta == '1':
            cursor.execute('''SELECT c.nome, SUM(s.importo) FROM spese s 
                              JOIN categorie c ON s.categoria_id = c.id GROUP BY c.nome''')
            print("\nCategoria........Totale Speso")
            for r in cursor.fetchall():
                print(f"{r[0]:<16} {r[1]:>10.2f}")

        elif scelta == '2':
            cursor.execute('''SELECT b.mese, c.nome, b.importo, SUM(s.importo)
                              FROM budget b JOIN categorie c ON b.categoria_id = c.id
                              LEFT JOIN spese s ON c.id = s.categoria_id AND strftime('%Y-%m', s.data) = b.mese
                              GROUP BY b.mese, c.id''')
            for r in cursor.fetchall():
                speso = r[3] if r[3] else 0
                stato = "⚠️ SUPERAMENTO BUDGET" if speso > r[2] else "✅ OK"
                print(f"\nMese: {r[0]} | Categoria: {r[1]}\nBudget: {r[2]} | Speso: {speso}\nStato: {stato}")

        elif scelta == '3':
            cursor.execute('''SELECT s.data, c.nome, s.importo, s.descrizione FROM spese s 
                              JOIN categorie c ON s.categoria_id = c.id ORDER BY s.data''')
            print("\nData        Categoria    Importo   Descrizione")
            for r in cursor.fetchall():
                print(f"{r[0]}  {r[1]:<12} {r[2]:>8.2f}  {r[3]}")

        elif scelta == '4':
            break

def menu_principale():
    conn = inizializza_db()
    while True:
        print("\n--- SISTEMA SPESE PERSONALI ---")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        
        scelta = input("Inserisci la tua scelta: ")
        
        if scelta == '1': gestione_categorie(conn)
        elif scelta == '2': inserisci_spesa(conn)
        elif scelta == '3': definisci_budget(conn)
        elif scelta == '4': visualizza_report(conn)
        elif scelta == '5':
            print("Uscita in corso..."); conn.close(); break
        else:
            print("⚠️ Scelta non valida. Riprovare.")

if __name__ == "__main__":
    menu_principale()
