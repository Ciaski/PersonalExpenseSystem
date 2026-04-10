CREATE TABLE categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL CHECK(length(nome) > 0)
);

CREATE TABLE spese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    importo REAL NOT NULL CHECK(importo > 0),
    categoria_id INTEGER NOT NULL,
    descrizione TEXT,
    FOREIGN KEY (categoria_id) REFERENCES categorie(id)
);

CREATE TABLE budget (
    mese TEXT NOT NULL, 
    categoria_id INTEGER NOT NULL, 
    importo REAL NOT NULL CHECK(importo > 0),
    PRIMARY KEY (mese, categoria_id),
    FOREIGN KEY (categoria_id) REFERENCES categorie(id)
);

-- Dati di esempio obbligatori
INSERT INTO categorie (nome) VALUES ('Cibo'), ('Trasporti'), ('Svago');
INSERT INTO budget (mese, categoria_id, importo) VALUES ('2024-05', 1, 300.00);
