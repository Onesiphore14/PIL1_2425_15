-- Base de données IFRI_comotorage
-- Création des tables principales

-- Table des utilisateurs
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telephone VARCHAR(15) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'passager' CHECK (role IN ('conducteur', 'passager')),
    photo_profil VARCHAR(255),
    point_depart VARCHAR(255),
    horaire_depart_habituel TIME,
    horaire_arrivee_habituel TIME,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME
);

-- Table des véhicules (pour les conducteurs)
CREATE TABLE vehicules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    marque VARCHAR(50) NOT NULL,
    modele VARCHAR(50) NOT NULL,
    nombre_places INTEGER NOT NULL DEFAULT 4,
    couleur VARCHAR(30),
    plaque VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des offres de covoiturage
CREATE TABLE offres_covoiturage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conducteur_id INTEGER NOT NULL,
    point_depart VARCHAR(255) NOT NULL,
    point_arrivee VARCHAR(255) NOT NULL,
    heure_depart DATETIME NOT NULL,
    places_disponibles INTEGER NOT NULL,
    prix DECIMAL(10,2) DEFAULT 0.00,
    description TEXT,
    statut VARCHAR(20) DEFAULT 'active' CHECK (statut IN ('active', 'complete', 'annulee')),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conducteur_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des demandes de covoiturage
CREATE TABLE demandes_covoiturage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passager_id INTEGER NOT NULL,
    point_depart VARCHAR(255) NOT NULL,
    point_arrivee VARCHAR(255) NOT NULL,
    heure_depart_souhaitee DATETIME NOT NULL,
    nombre_places_demandees INTEGER DEFAULT 1,
    description TEXT,
    statut VARCHAR(20) DEFAULT 'active' CHECK (statut IN ('active', 'satisfaite', 'annulee')),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (passager_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des correspondances (matching)
CREATE TABLE correspondances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    offre_id INTEGER NOT NULL,
    demande_id INTEGER NOT NULL,
    conducteur_id INTEGER NOT NULL,
    passager_id INTEGER NOT NULL,
    score_compatibilite DECIMAL(5,2),
    statut VARCHAR(20) DEFAULT 'proposee' CHECK (statut IN ('proposee', 'acceptee', 'refusee', 'confirmee')),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_confirmation DATETIME,
    FOREIGN KEY (offre_id) REFERENCES offres_covoiturage(id) ON DELETE CASCADE,
    FOREIGN KEY (demande_id) REFERENCES demandes_covoiturage(id) ON DELETE CASCADE,
    FOREIGN KEY (conducteur_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (passager_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des conversations
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correspondance_id INTEGER NOT NULL,
    nom_conversation VARCHAR(100),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_activite DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (correspondance_id) REFERENCES correspondances(id) ON DELETE CASCADE
);

-- Table des messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    expediteur_id INTEGER NOT NULL,
    contenu TEXT NOT NULL,
    date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
    lu BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (expediteur_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des participants aux conversations
CREATE TABLE participants_conversation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_lecture DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(conversation_id, user_id)
);

-- Index pour optimiser les performances
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_telephone ON users(telephone);
CREATE INDEX idx_offres_conducteur ON offres_covoiturage(conducteur_id);
CREATE INDEX idx_demandes_passager ON demandes_covoiturage(passager_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_expediteur ON messages(expediteur_id);
CREATE INDEX idx_correspondances_offre ON correspondances(offre_id);
CREATE INDEX idx_correspondances_demande ON correspondances(demande_id);