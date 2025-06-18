import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ifri_comotorage.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            role TEXT CHECK(role IN ('conducteur', 'passager')) NOT NULL,
            point_depart TEXT,
            horaires TEXT,
            vehicule_info TEXT,
            photo TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conducteur_id INTEGER,
            depart TEXT NOT NULL,
            destination TEXT NOT NULL,
            jour TEXT NOT NULL,
            horaires TEXT,
            places_disponibles INTEGER,
            FOREIGN KEY (conducteur_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()