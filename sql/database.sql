PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL CHECK(length(nome) > 0)
);

CREATE TABLE IF NOT EXISTS spese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_spesa TEXT NOT NULL,
    cifra REAL NOT NULL CHECK(cifra > 0),
    nota TEXT,
    cat_id INTEGER NOT NULL,
    FOREIGN KEY (cat_id) REFERENCES categorie(id)
);
CREATE TABLE IF NOT EXISTS budget_mensile (
    mese_rif TEXT NOT NULL, 
    cat_id INTEGER NOT NULL, 
    limite_max REAL NOT NULL CHECK(limite_max > 0),
    PRIMARY KEY (mese_rif, cat_id),
    FOREIGN KEY (cat_id) REFERENCES categorie(id)
);
-- Inserimento Categorie
INSERT INTO categorie (nome) VALUES ('Alimentari');
INSERT INTO categorie (nome) VALUES ('Trasporti');
INSERT INTO categorie (nome) VALUES ('Svago');

-- Inserimento Budget per Aprile 2026
INSERT INTO budget_mensile (mese_rif, cat_id, limite_max) VALUES ('2026-04', 1, 200.00);
INSERT INTO budget_mensile (mese_rif, cat_id, limite_max) VALUES ('2026-04', 2, 50.00);

-- Inserimento Spese di esempio
INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES ('2026-04-10', 45.50, 'Spesa Esselunga', 1);
INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES ('2026-04-12', 60.00, 'Rifornimento Benzina', 2); -- Esempio di sforamento budget
