import sqlite3
import os

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
    titolo = input("Inserisci il nome della categoria da creare: ").strip().capitalize()
    if not titolo:
        print("[-] Errore: Il nome non può essere vuoto.")
        return
    try:
        cmd = db.cursor()
        cmd.execute("INSERT INTO categorie (nome) VALUES (?)", (titolo,))
        db.commit()
        print(f"[+] Ottimo! La categoria '{titolo}' è stata salvata.")
    except sqlite3.IntegrityError:
        print(f"[-] Attenzione: '{titolo}' è già presente nel sistema.")

def registra_transazione(db):
    print("\n--- REGISTRAZIONE NUOVA SPESA ---")
    data_ins = input("Data dell'operazione (AAAA-MM-GG): ")
    try:
        valore = float(input("Importo speso: "))
        if valore <= 0:
            print("[-] Errore: L'importo deve essere una cifra positiva.")
            return
    except ValueError:
        print("[-] Errore: Inserire un valore numerico valido.")
        return

    etichetta_cat = input("Categoria di riferimento: ").strip().capitalize()
    memo = input("Nota aggiuntiva (opzionale): ")
    
    cmd = db.cursor()
    cmd.execute("SELECT id FROM categorie WHERE nome = ?", (etichetta_cat,))
    record_cat = cmd.fetchone()
    
    if record_cat:
        cmd.execute("INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES (?, ?, ?, ?)", 
                    (data_ins, valore, memo, record_cat[0]))
        db.commit()
        print("[OK] Transazione registrata con successo.")
    else:
        print(f"[-] Errore: La categoria '{etichetta_cat}' non esiste. Creala prima.")

def definisci_budget_mensile(db):
    print("\n--- IMPOSTAZIONE BUDGET ---")
    periodo = input("Inserisci il mese (AAAA-MM): ")
    cat_nome = input("Categoria di riferimento: ").strip().capitalize()
    try:
        limite = float(input("Inserisci il limite massimo di spesa: "))
        if limite <= 0:
            print("[-] Errore: Il budget deve essere maggiore di zero.")
            return
        
        cmd = db.cursor()
        cmd.execute("SELECT id FROM categorie WHERE nome = ?", (cat_nome,))
        res = cmd.fetchone()
        
        if res:
            cmd.execute("INSERT OR REPLACE INTO budget_mensile VALUES (?, ?, ?)", 
                        (periodo, res[0], limite))
            db.commit()
            print(f"[+] Budget per {cat_nome} impostato correttamente.")
        else:
            print("[-] Errore: Categoria non trovata.")
    except ValueError:
        print("[-] Errore: Inserire un numero valido.")

def sottomenu_statistiche(db):
    while True:
        print("\n--- CENTRO ANALISI E REPORT ---")
        print("1. Riepilogo totale per ogni categoria")
        print("2. Confronto Spese vs Budget Mensile")
        print("3. Storico completo movimenti")
        print("4. Torna al menù principale")
        
        scelta_rep = input("\nQuale analisi vuoi visualizzare? ")
        cmd = db.cursor()

        if scelta_rep == '1':
            cmd.execute('''SELECT c.nome, SUM(s.cifra) FROM spese s 
                           JOIN categorie c ON s.cat_id = c.id GROUP BY c.id''')
            print("\n{:<20} {:>12}".format("CATEGORIA", "TOTALE SPESO"))
            print("-" * 35)
            for r in cmd.fetchall(): print("{:<20} {:>10.2f}€".format(r[0], r[1]))

        elif scelta_rep == '2':
            cmd.execute('''SELECT b.mese_rif, c.nome, b.limite_max, IFNULL(SUM(s.cifra), 0)
                           FROM budget_mensile b JOIN categorie c ON b.cat_id = c.id
                           LEFT JOIN spese s ON c.id = s.cat_id AND strftime('%Y-%m', s.data_spesa) = b.mese_rif
                           GROUP BY b.mese_rif, c.id''')
            print("\nANALISI BUDGET:")
            for r in cmd.fetchall():
                alert = "!! SFORATO !!" if r[3] > r[2] else "In linea"
                print(f"[{r[0]}] {r[1]}: Spesi {r[3]}€ su {r[2]}€ ({alert})")

        elif scelta_rep == '3':
            cmd.execute('''SELECT s.data_spesa, c.nome, s.cifra, s.nota FROM spese s 
                           JOIN categorie c ON s.cat_id = c.id ORDER BY s.data_spesa DESC''')
            print("\n{:<12} | {:<15} | {:>8} | {:<20}".format("DATA", "CAT.", "EURO", "NOTE"))
            print("-" * 65)
            for r in cmd.fetchall(): print("{:<12} | {:<15} | {:>8.2f} | {:<20}".format(r[0], r[1], r[2], r[3] or ""))

        elif scelta_rep == '4': break
        else: print("Scelta non valida, riprova.")

def main_app():
    connessione = inizializza_sistema()
    while True:
        print("\n==========================================")
        print("     WALLET MANAGER - GESTIONE SPESE      ")
        print("==========================================")
        print("1. Gestisci Categorie")
        print("2. Registra una Spesa")
        print("3. Imposta Budget Mensile")
        print("4. Visualizza Statistiche e Report")
        print("5. Esci dall'applicazione")
        
        scelta = input("\nSeleziona un'opzione: ")
        
        if scelta == '1': 
            aggiungi_nuova_categoria(connessione)
        elif scelta == '2': 
            registra_transazione(connessione)
        elif scelta == '3': 
            definisci_budget_mensile(connessione) 
        elif scelta == '4': 
            sottomenu_statistiche(connessione)
        elif scelta == '5': 
            print("Salvataggio dati in corso... Arrivederci!")
            break
        else: 
            print("Comando non riconosciuto.")
            
    connessione.close()

if __name__ == "__main__":
    main_app()
