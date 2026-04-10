import sqlite3

def inizializza_db():
    conn = sqlite3.connect('Spese_Personali.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('''CREATE TABLE IF NOT EXISTS categorie (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT UNIQUE NOT NULL CHECK(length(nome) > 0))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS spese (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT NOT NULL,
                        importo REAL NOT NULL CHECK(importo > 0),
                        categoria_id INTEGER NOT NULL,
                        FOREIGN KEY (categoria_id) REFERENCES categorie(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (
                        mese TEXT NOT NULL, 
                        categoria_id INTEGER NOT NULL, 
                        importo_limite REAL NOT NULL CHECK(importo_limite > 0),
                        PRIMARY KEY (mese, categoria_id),
                        FOREIGN KEY (categoria_id) REFERENCES categorie(id))''')
    conn.commit()
    return conn

def gestione_categorie(conn):
    nome = input("Nuova categoria: ").strip()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("✅ Categoria aggiunta.")
    except: print("❌ Errore: Categoria già esistente o non valida.")

def inserisci_spesa(conn):
    data = input("Data (YYYY-MM-DD): ")
    cat = input("Nome categoria: ")
    try:
        imp = float(input("Importo speso: "))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorie WHERE nome = ?", (cat,))
        res = cursor.fetchone()
        if res:
            cursor.execute("INSERT INTO spese (data, importo, categoria_id) VALUES (?, ?, ?)", (data, imp, res[0]))
            conn.commit()
            print("✅ Spesa registrata.")
        else: print("❌ Categoria non trovata.")
    except: print("❌ Errore dati inseriti.")

def definisci_budget(conn):
    mese = input("Mese (YYYY-MM): ")
    cat = input("Nome categoria: ")
    try:
        limite = float(input("Limite di spesa (Budget): "))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorie WHERE nome = ?", (cat,))
        res = cursor.fetchone()
        if res:
            cursor.execute("INSERT OR REPLACE INTO budget VALUES (?, ?, ?)", (mese, res[0], limite))
            conn.commit()
            print(f"✅ Budget per {cat} impostato a {limite}€.")
        else: print("❌ Categoria non trovata.")
    except: print("❌ Errore inserimento budget.")

def report_confronto_budget(conn):
    cursor = conn.cursor()
    print("\n--- REPORT CONFRONTO BUDGET ---")
    query = '''
        SELECT b.mese, c.nome, b.importo_limite, IFNULL(SUM(s.importo), 0)
        FROM budget b
        JOIN categorie c ON b.categoria_id = c.id
        LEFT JOIN spese s ON c.id = s.categoria_id AND strftime('%Y-%m', s.data) = b.mese
        GROUP BY b.mese, c.id
    '''
    cursor.execute(query)
    for r in cursor.fetchall():
        stato = "⚠️ SUPERAMENTO!" if r[3] > r[2] else "✅ OK"
        print(f"Mese: {r[0]} | Cat: {r[1]} | Budget: {r[2]}€ | Speso: {r[3]}€ | {stato}")

def menu():
    conn = inizializza_db()
    print("*" * 40)
    print("  BENVENUTO NEL SISTEMA SPESE PERSONALI  ")
    print("*" * 40)
    while True:
        print("\n1. Gestione Categorie\n2. Inserisci Spesa\n3. Definisci Budget\n4. Report Budget vs Spese\n5. Esci")
        scelta = input("Scegli un'opzione: ")
        if scelta == '1': gestione_categorie(conn)
        elif scelta == '2': inserisci_spesa(conn)
        elif scelta == '3': definisci_budget(conn)
        elif scelta == '4': report_confronto_budget(conn)
        elif scelta == '5': break
    conn.close()

if __name__ == "__main__":
    menu()

