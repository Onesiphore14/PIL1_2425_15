-- ceci est le sql qui presente la structure de la base de donné du groupe 15
-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    telephone TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('conducteur', 'passager')),
    photo TEXT DEFAULT 'Base.png',

    -- Infos optionnelles
    vehicule_marque TEXT,
    vehicule_modele TEXT,
    places INTEGER,
    depart TEXT,
    heure_depart TEXT,
    heure_arrivee TEXT
);

-- Table des trajets publiés
CREATE TABLE IF NOT EXISTS rides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('offer', 'request')),
    departure TEXT NOT NULL,
    arrival TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    seats INTEGER,
    comments TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Table des conversations
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_id) REFERENCES users(id),
    FOREIGN KEY (user2_id) REFERENCES users(id)
);

-- Table des messages
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (sender_id) REFERENCES users(id)
);