import sqlite3

def inizializza_sistema():
    db = sqlite3.connect('Spese_Personali.db')
    cmd = db.cursor()
    cmd.execute("PRAGMA foreign_keys = ON;") 
    cmd.execute('''CREATE TABLE IF NOT EXISTS categorie (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT UNIQUE NOT NULL CHECK(length(nome) > 0))''')
    
    cmd.execute('''CREATE TABLE IF NOT EXISTS spese (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_spesa TEXT NOT NULL,
                        cifra REAL NOT NULL CHECK(cifra > 0),
                        nota TEXT,
                        cat_id INTEGER NOT NULL,
                        FOREIGN KEY (cat_id) REFERENCES categorie(id))''')
    
    cmd.execute('''CREATE TABLE IF NOT EXISTS budget_mensile (
                        mese_rif TEXT NOT NULL, 
                        cat_id INTEGER NOT NULL, 
                        limite_max REAL NOT NULL CHECK(limite_max > 0),
                        PRIMARY KEY (mese_rif, cat_id),
                        FOREIGN KEY (cat_id) REFERENCES categorie(id))''')
    db.commit()
    return db

def aggiungi_nuova_categoria(db):
    titolo = input("Nome della categoria (stringa): ").strip().capitalize()
    if not titolo: return 
    try:
        cmd = db.cursor()
        cmd.execute("INSERT INTO categorie (nome) VALUES (?)", (titolo,))
        db.commit()
        print("Categoria inserita correttamente.") 
    except sqlite3.IntegrityError:
        print("La categoria esiste già.") 
def registra_transazione(db):
    data_ins = input("Data (formato YYYY-MM-DD): ")
    try:
        valore = float(input("Importo: "))
        if valore <= 0:
            print("Errore: l’importo deve essere maggiore di zero.") 
            return
    except ValueError: 
        print("Errore: inserire un numero valido.")
        return

    cat_nome = input("Nome della categoria: ").strip().capitalize()
    memo = input("Descrizione facoltativa: ")
    
    cmd = db.cursor()
    cmd.execute("SELECT id FROM categorie WHERE nome = ?", (cat_nome,))
    res = cmd.fetchone()
    
    if res:
        cmd.execute("INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES (?, ?, ?, ?)", 
                    (data_ins, valore, memo, res[0]))
        db.commit()
        print("Spesa inserita correttamente.") 
    else:
        print("Errore: la categoria non esiste.") 

def definisci_budget_mensile(db):
    periodo = input("Mese (YYYY-MM): ")
    cat_nome = input("Nome della categoria: ").strip().capitalize()
    try:
        limite = float(input("Importo del budget: "))
        if limite <= 0: return
        
        cmd = db.cursor()
        cmd.execute("SELECT id FROM categorie WHERE nome = ?", (cat_nome,))
        res = cmd.fetchone()
        
        if res:
            # Uso di INSERT OR REPLACE come richiesto dal Modulo 3
            cmd.execute("INSERT OR REPLACE INTO budget_mensile (mese_rif, cat_id, limite_max) VALUES (?, ?, ?)", 
                        (periodo, res[0], limite))
            db.commit()
            print("Budget mensile salvato correttamente.") 
        else:
            print("Errore: la categoria non esiste.")
    except ValueError: pass

def sottomenu_statistiche(db):
    while True:
        print("\nMenu dei Report") # Obbligatorio Pag. 5
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")
        
        scelta = input("Inserisci la tua scelta: ")
        cmd = db.cursor()

        if scelta == '1':
            cmd.execute("SELECT c.nome, SUM(s.cifra) FROM spese s JOIN categorie c ON s.cat_id = c.id GROUP BY c.nome")
            print("\nCategoria........Totale Speso")
            for r in cmd.fetchall(): print(f"{r[0]:.<17}{r[1]:.2f}")

        elif scelta == '2':
            cmd.execute('''SELECT b.mese_rif, c.nome, b.limite_max, IFNULL(SUM(s.cifra), 0)
                           FROM budget_mensile b JOIN categorie c ON b.cat_id = c.id
                           LEFT JOIN spese s ON c.id = s.cat_id AND strftime('%Y-%m', s.data_spesa) = b.mese_rif
                           GROUP BY b.mese_rif, c.id''')
            for r in cmd.fetchall():
                stato = "SUPERAMENTO BUDGET" if r[3] > r[2] else "OK"
                print(f"\nMese: {r[0]}\nCategoria: {r[1]}\nBudget: {r[2]}\nSpeso: {r[3]}\nStato: {stato}")

        elif scelta == '3':
            cmd.execute("SELECT s.data_spesa, c.nome, s.cifra, s.nota FROM spese s JOIN categorie c ON s.cat_id = c.id ORDER BY s.data_spesa ASC")
            print("\nData Categoria Importo Descrizione")
            print("-" * 50)
            for r in cmd.fetchall(): print(f"{r[0]} {r[1]} {r[2]:.2f} {r[3] or ''}")

        elif scelta == '4': break
        else: print("Scelta non valida. Riprovare.")

def main_app():
    connessione = inizializza_sistema()
    print("Benvenuto nel sistema di gestione spese!")     
    while True:
        print("\n-------------------------")
        print("SISTEMA SPESE PERSONALI")
        print("-------------------------")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        print("-------------------------")
        
        scelta = input("Inserisci la tua scelta: ")
        
        if scelta == '1': aggiungi_nuova_categoria(connessione)
        elif scelta == '2': registra_transazione(connessione)
        elif scelta == '3': definisci_budget_mensile(connessione)
        elif scelta == '4': sottomenu_statistiche(connessione)
        elif scelta == '5': break
        else: print("Scelta non valida. Riprovare.")             
    connessione.close()

if __name__ == "__main__":
    main_app()
