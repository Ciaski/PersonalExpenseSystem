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
INSERT INTO categorie (nome) VALUES ('Alimentari');
INSERT INTO categorie (nome) VALUES ('Trasporti');
INSERT INTO categorie (nome) VALUES ('Svago');
INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES ('2026-04-01', 55.40, 'Spesa supermercato', 1);
INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES ('2026-04-02', 20.00, 'Ricarica abbonamento bus', 2);
INSERT INTO spese (data_spesa, cifra, nota, cat_id) VALUES ('2026-04-05', 15.50, 'Pizza con amici', 3);
INSERT INTO budget_mensile (mese_rif, cat_id, limite_max) VALUES ('2026-04', 1, 300.00);
INSERT INTO budget_mensile (mese_rif, cat_id, limite_max) VALUES ('2026-04', 2, 50.00);
