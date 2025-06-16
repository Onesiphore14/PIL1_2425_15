import sqlite3
import hashlib

class DatabaseManager:
    def __init__(self, db_name="ifri_comotorage.db"):
        self.db_name = db_name
        self.create_tables()
        
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Table users avec la nouvelle structure complète
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
            
            # Table vehicules (si vous en avez besoin)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marque TEXT NOT NULL,
                modele TEXT NOT NULL,
                places INTEGER NOT NULL,
                couleur TEXT,
                numero_plaque TEXT UNIQUE,
                conducteur_id INTEGER,
                FOREIGN KEY (conducteur_id) REFERENCES users(id)
            )
            ''')
            
            # Table trajets pour gérer les courses
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS trajets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conducteur_id INTEGER NOT NULL,
                point_depart TEXT NOT NULL,
                point_arrivee TEXT NOT NULL,
                heure_depart TEXT NOT NULL,
                heure_arrivee TEXT,
                places_disponibles INTEGER NOT NULL,
                prix REAL,
                date_trajet DATE NOT NULL,
                statut TEXT DEFAULT 'actif',
                FOREIGN KEY (conducteur_id) REFERENCES users(id)
            )
            ''')
            
            # Table reservations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trajet_id INTEGER NOT NULL,
                passager_id INTEGER NOT NULL,
                nb_places INTEGER DEFAULT 1,
                statut TEXT DEFAULT 'confirmee',
                date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trajet_id) REFERENCES trajets(id),
                FOREIGN KEY (passager_id) REFERENCES users(id)
            )
            ''')
            
            conn.commit()
            print("Toutes les tables créées avec succès!")
            
        except Exception as e:
            print(f"Erreur lors de la création des tables: {e}")
        finally:
            conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def insert_sample_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si des données existent déjà
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count > 0:
                print("Des données existent déjà dans la base.")
                return
            
            # Données d'exemple mises à jour avec la nouvelle structure
            users_data = [
                ('Adjovi', 'Kossou', 'adjovi.kossou@gmail.com', '97123456', self.hash_password('password123'), 'conducteur', 'Cotonou Centre', '7h-9h, 17h-19h', 'Toyota Corolla bleue, AB-123-CD', None),
                ('Tchedre', 'Mama', 'tchedre.mama@yahoo.fr', '96654321', self.hash_password('motdepasse'), 'passager', 'Calavi Campus', '8h-9h', None, None),
                ('Sessi', 'Dodji', 'sessi.dodji@hotmail.com', '95987654', self.hash_password('secure123'), 'conducteur', 'Akpakpa', '6h-8h, 16h-18h', 'Bus Mercedes 18 places, BC-456-EF', None)
            ]
            
            cursor = conn.cursor()
            for user in users_data:
                cursor.execute('''
                INSERT INTO users (nom, prenom, email, telephone, mot_de_passe, role, 
                                 point_depart, horaires, vehicule_info, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', user)
            
            # Données des véhicules
            vehicules_data = [
                (1, 'Toyota', 'Corolla', 4, 'Blanc', 'AB-123-CD'),
                (3, 'Mercedes', 'Sprinter', 18, 'Blanc', 'BC-456-EF')
            ]
            
            for vehicule in vehicules_data:
                cursor.execute('''
                INSERT INTO vehicules (conducteur_id, marque, modele, places, couleur, numero_plaque)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', vehicule)
            
            conn.commit()
            print("Données d'exemple insérées avec succès!")
            
        except Exception as e:
            print(f"Erreur lors de l'insertion des données: {e}")
        finally:
            conn.close()
    
    # ========== NOUVELLES FONCTIONS POUR LA GESTION UTILISATEURS ==========
    
    def add_user(self, nom, prenom, telephone, email, mot_de_passe, role, 
                 point_depart=None, horaires=None, vehicule_info=None, photo=None):
        """Ajoute un nouvel utilisateur avec la nouvelle structure"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(mot_de_passe)
            
            cursor.execute('''
            INSERT INTO users (nom, prenom, telephone, email, mot_de_passe, role, 
                             point_depart, horaires, vehicule_info, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nom, prenom, telephone, email, hashed_password, role,
                  point_depart, horaires, vehicule_info, photo))
            
            conn.commit()
            user_id = cursor.lastrowid
            return True, f"Utilisateur ajouté avec l'ID: {user_id}"
            
        except sqlite3.IntegrityError as e:
            if "telephone" in str(e):
                return False, "Ce numéro de téléphone existe déjà"
            elif "email" in str(e):
                return False, "Cet email existe déjà"
            else:
                return False, f"Erreur d'intégrité: {e}"
        except Exception as e:
            return False, f"Erreur lors de l'ajout: {e}"
        finally:
            conn.close()
    
    def authenticate_user(self, email, mot_de_passe):
        """Authentifie un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(mot_de_passe)
            
            cursor.execute('''
            SELECT id, nom, prenom, role, point_depart, horaires, vehicule_info 
            FROM users WHERE email = ? AND mot_de_passe = ?
            ''', (email, hashed_password))
            
            user = cursor.fetchone()
            
            if user:
                return True, {
                    'id': user[0],
                    'nom': user[1],
                    'prenom': user[2],
                    'role': user[3],
                    'point_depart': user[4],
                    'horaires': user[5],
                    'vehicule_info': user[6]
                }
            else:
                return False, "Email ou mot de passe incorrect"
                
        except Exception as e:
            return False, f"Erreur lors de l'authentification: {e}"
        finally:
            conn.close()
    
    def get_conducteurs(self):
        """Récupère tous les conducteurs avec leurs informations complètes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, nom, prenom, telephone, email, point_depart, 
                   horaires, vehicule_info, photo
            FROM users WHERE role = 'conducteur'
            ORDER BY nom, prenom
            ''')
            
            conducteurs = cursor.fetchall()
            
            result = []
            for c in conducteurs:
                result.append({
                    'id': c[0],
                    'nom': c[1],
                    'prenom': c[2],
                    'telephone': c[3],
                    'email': c[4],
                    'point_depart': c[5],
                    'horaires': c[6],
                    'vehicule_info': c[7],
                    'photo': c[8]
                })
            
            return result
            
        except Exception as e:
            print(f"Erreur lors de la récupération des conducteurs: {e}")
            return []
        finally:
            conn.close()
    
    def get_passagers(self):
        """Récupère tous les passagers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, nom, prenom, telephone, email, point_depart, horaires, photo
            FROM users WHERE role = 'passager'
            ORDER BY nom, prenom
            ''')
            
            passagers = cursor.fetchall()
            
            result = []
            for p in passagers:
                result.append({
                    'id': p[0],
                    'nom': p[1],
                    'prenom': p[2],
                    'telephone': p[3],
                    'email': p[4],
                    'point_depart': p[5],
                    'horaires': p[6],
                    'photo': p[7]
                })
            
            return result
            
        except Exception as e:
            print(f"Erreur lors de la récupération des passagers: {e}")
            return []
        finally:
            conn.close()
    
    def update_user(self, user_id, **kwargs):
        """Met à jour les informations d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Champs autorisés à la mise à jour
            allowed_fields = ['nom', 'prenom', 'telephone', 'email', 'point_depart', 
                            'horaires', 'vehicule_info', 'photo']
            
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return False, "Aucun champ valide à mettre à jour"
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            values.append(user_id)
            
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Utilisateur mis à jour avec succès"
            else:
                return False, "Utilisateur non trouvé"
                
        except sqlite3.IntegrityError as e:
            return False, f"Erreur d'intégrité: {e}"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {e}"
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, nom, prenom, telephone, email, role, point_depart, 
                   horaires, vehicule_info, photo FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'nom': user[1],
                    'prenom': user[2],
                    'telephone': user[3],
                    'email': user[4],
                    'role': user[5],
                    'point_depart': user[6],
                    'horaires': user[7],
                    'vehicule_info': user[8],
                    'photo': user[9]
                }
            return None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
        finally:
            conn.close()

# Test de la nouvelle structure
if __name__ == "__main__":
    print("Initialisation de la base de données IFRI Comotorage...")
    db = DatabaseManager()
    
    print("\n=== Insertion des données d'exemple ===")
    db.insert_sample_data()
    
    print("\n=== Test d'authentification ===")
    success, result = db.authenticate_user("adjovi.kossou@gmail.com", "password123")
    if success:
        print(f"✅ Connexion réussie: {result['nom']} {result['prenom']} ({result['role']})")
        print(f"   Point de départ: {result['point_depart']}")
        print(f"   Horaires: {result['horaires']}")
        if result['vehicule_info']:
            print(f"   Véhicule: {result['vehicule_info']}")
    else:
        print(f"❌ Échec de connexion: {result}")
    
    print("\n=== Liste des conducteurs ===")
    conducteurs = db.get_conducteurs()
    for c in conducteurs:
        print(f"🚗 {c['nom']} {c['prenom']}")
        print(f"   📍 Départ: {c['point_depart']}")
        print(f"   🕒 Horaires: {c['horaires']}")
        print(f"   🚙 Véhicule: {c['vehicule_info']}")
        print(f"   📞 Tél: {c['telephone']}")
        print()
    
    print("\n=== Liste des passagers ===")
    passagers = db.get_passagers()
    for p in passagers:
        print(f"👤 {p['nom']} {p['prenom']}")
        print(f"   📍 Départ: {p['point_depart']}")
        print(f"   🕒 Horaires: {p['horaires']}")
        print(f"   📞 Tél: {p['telephone']}")
        print()
    
    print("\n=== Test d'ajout d'un nouvel utilisateur ===")
    success, message = db.add_user(
        nom="Nouveau",
        prenom="Conducteur", 
        telephone="90000000",
        email="nouveau@test.com",
        mot_de_passe="test123",
        role="conducteur",
        point_depart="Godomey",
        horaires="7h30-9h30",
        vehicule_info="Peugeot 307 grise, 5 places"
    )
    print(f"{'✅' if success else '❌'} {message}")
    
    print("\nUtilisez les fonctions pour ajouter des utilisateurs.")

