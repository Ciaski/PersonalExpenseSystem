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
                        descrizione TEXT,
                        FOREIGN KEY (categoria_id) REFERENCES categorie(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (
                        mese TEXT NOT NULL, 
                        categoria_id INTEGER NOT NULL, 
                        importo REAL NOT NULL CHECK(importo > 0),
                        PRIMARY KEY (mese, categoria_id),
                        FOREIGN KEY (categoria_id) REFERENCES categorie(id))''')
    conn.commit()
    return conn

def gestione_categorie(conn):
    nome = input("Nome categoria: ").strip()
    if not nome: return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("✅ Categoria aggiunta.")
    except: print("❌ Errore (esiste già o vuota).")

def inserisci_spesa(conn):
    data = input("Data (YYYY-MM-DD): ")
    cat = input("Nome categoria: ")
    try:
        imp = float(input("Importo: "))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categorie WHERE nome = ?", (cat,))
        res = cursor.fetchone()
        if res:
            cursor.execute("INSERT INTO spese (data, importo, categoria_id) VALUES (?, ?, ?)", (data, imp, res[0]))
            conn.commit()
            print("✅ Spesa registrata.")
        else: print("❌ Categoria inesistente.")
    except: print("❌ Errore nell'importo.")

def visualizza_report(conn):
    cursor = conn.cursor()
    print("\n--- REPORT SPESE ---")
    cursor.execute("SELECT c.nome, SUM(s.importo) FROM spese s JOIN categorie c ON s.categoria_id = c.id GROUP BY c.nome")
    for r in cursor.fetchall(): print(f"{r[0]}: {r[1]}€")

def menu():
    conn = inizializza_db()
    print("*" * 40)
    print("  BENVENUTO NEL SISTEMA SPESE PERSONALI  ")
    print("*" * 40)
    
    while True:
        print("\n1. Aggiungi Categoria\n2. Inserisci Spesa\n3. Report\n4. Esci")
        scelta = input("Scelta: ")
        if scelta == '1': gestione_categorie(conn)
        elif scelta == '2': inserisci_spesa(conn)
        elif scelta == '3': visualizza_report(conn)
        elif scelta == '4': 
            print("\nGrazie per aver usato il sistema. Arrivederci!")
            break
    conn.close()

if __name__ == "__main__":
    menu()
