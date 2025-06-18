
from flask import Flask, request, jsonify ,send_from_directory
from flask_cors import CORS
from database.connection import get_connection, init_db
from werkzeug.utils import secure_filename
import os
from backend.routes.messaging import messaging_routes


app = Flask(__name__)
CORS(app)

app.register_blueprint(messaging_routes)

@app.route('/')
def start():
    return "Backend avec Canisius et Abdoul"

#la route pour l'inscription
@app.route('/register', methods=['POST'])
def register():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    telephone = request.form.get('telephone')
    email = request.form.get('email')
    mot_de_passe = request.form.get('mot_de_passe')
    role = request.form.get('role')

    if not all([nom, prenom, telephone, email, mot_de_passe, role]):
        return ""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? OR telephone = ?", (email, telephone))
    if cursor.fetchone():
        return "Email ou téléphone déjà utilisé", 409

    cursor.execute('''
        INSERT INTO users (nom, prenom, telephone, email, mot_de_passe, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nom, prenom, telephone, email, mot_de_passe, role))

    conn.commit()
    conn.close()

    return ""

#celle pour la photo de profile
@app.route('/uploads/<filename>')
def serve_upload(filename):
    upload_folder = os.path.join('frontend', 'uploads')
    return send_from_directory(upload_folder, filename)



#Celle pour la conexion
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    mot_de_passe = request.form.get('mot_de_passe')

    if not email or not mot_de_passe:
        return "Champs requis", 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and user['mot_de_passe'] == mot_de_passe:
        return jsonify({
            "message": f"Bienvenue, {user['prenom']} !",
            "id": user['id']
        }), 200
    else:
        return "Identifiants invalides", 401


#la route pour la réinitialisation du mot de passe
@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    nouveau_mdp = request.form.get('nouveau_mot_de_passe')

    if not email or not nouveau_mdp:
        return "Champs requis", 400

    conn = get_connection()
    cursor = conn.cursor()

    # Vérifie que l'utilisateur existe
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "Utilisateur non trouvé", 404

    # Met à jour le mot de passe
    cursor.execute("UPDATE users SET mot_de_passe = ? WHERE email = ?", (nouveau_mdp, email))
    conn.commit()
    conn.close()

    return "Mot de passe modifié", 200

#La route pour la creation du profile

@app.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, nom, prenom, telephone, email, role, point_depart, horaires, vehicule_info, photo
        FROM users WHERE id = ?
    ''', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        profile = {key: user[key] for key in user.keys()}
        return jsonify(profile), 200
    else:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

#mise à jour du profile
@app.route('/profile/update/<int:user_id>', methods=['POST'])
def update_profile(user_id):
    point_depart = request.form.get('point_depart')
    horaires = request.form.get('horaires')
    vehicule_info = request.form.get('vehicule_info')

    # Gestion de la photo
    photo = request.files.get('photo')
    photo_filename = None

    if photo and photo.filename != "":
        filename = secure_filename(photo.filename)
        upload_folder = os.path.join('frontend', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        photo_path = os.path.join(upload_folder, filename)
        photo.save(photo_path)
        photo_filename = filename  # pour mise à jour SQL
    else:
        # On garde l'ancienne photo si aucune nouvelle n'est envoyée
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT photo FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        photo_filename = row['photo'] if row else None
        conn.close()

    # Mise à jour en base
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET point_depart = ?, horaires = ?, vehicule_info = ?, photo = ?
        WHERE id = ?
    ''', (point_depart, horaires, vehicule_info, photo_filename, user_id))

    conn.commit()
    conn.close()

    return "Profil mis à jour avec succès", 200


#la route pour la recherche de trajet
@app.route('/search', methods=['POST'])
def search_rides():
    depart = request.form.get('depart')
    destination = request.form.get('destination')
    jour = request.form.get('jour')

    if not all([depart, destination, jour]):
        return jsonify({'message': 'Champs requis'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.*, u.nom, u.prenom, u.telephone
        FROM rides r
        JOIN users u ON r.conducteur_id = u.id
        WHERE r.depart LIKE ? AND r.destination LIKE ? AND r.jour = ?
        ORDER BY r.jour ASC
    ''', (f'%{depart}%', f'%{destination}%', jour))

    rows = cursor.fetchall()
    conn.close()

    trajets = []
    for row in rows:
        trajets.append({
            'depart': row['depart'],
            'destination': row['destination'],
            'jour': row['jour'],
            'horaires': row['horaires'],
            'places_disponibles': row['places_disponibles'],
            'conducteur': {
                'nom': row['nom'],
                'prenom': row['prenom'],
                'telephone': row['telephone']
            }
        })

    return jsonify(trajets), 200
# Initiation de la base
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    