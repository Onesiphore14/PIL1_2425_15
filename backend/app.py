from flask import Flask, request, jsonify
from flask_cors import CORS
from database.connection import get_connection, init_db

app = Flask(__name__)
CORS(app)

# ----------- ROUTE : REGISTER ---------------
@app.route('/register', methods=['POST'])
def register():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    telephone = request.form.get('telephone')
    email = request.form.get('email')
    mot_de_passe = request.form.get('mot_de_passe')
    role = request.form.get('role')

    if not all([nom, prenom, telephone, email, mot_de_passe, role]):
        return "Champs manquants", 400

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

    return "Inscription réussie", 201

# ----------- ROUTE : LOGIN ------------------
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
        return f"Bienvenue, {user['prenom']} !", 200
    else:
        return "Identifiants invalides", 401

# ----------- ROUTE : GET PROFILE ------------
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

@app.route('/profile/update/<int:user_id>', methods=['POST'])
def update_profile(user_id):
    point_depart = request.form.get('point_depart')
    horaires = request.form.get('horaires')
    vehicule_info = request.form.get('vehicule_info')
    photo = request.form.get('photo')

    conn = get_connection()
    cursor = conn.cursor()

    # On met à jour uniquement les champs fournis
    cursor.execute('''
        UPDATE users
        SET point_depart = ?, horaires = ?, vehicule_info = ?, photo = ?
        WHERE id = ?
    ''', (point_depart, horaires, vehicule_info, photo, user_id))

    conn.commit()
    conn.close()

    return "Profil mis à jour avec succès", 200

@app.route('/search', methods=['POST'])
def search_rides():
    depart = request.form.get('depart')
    destination = request.form.get('destination')
    jour = request.form.get('jour')

    if not all([depart, destination, jour]):
        return "Champs requis", 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.*, u.nom, u.prenom, u.telephone
        FROM rides r
        JOIN users u ON r.conducteur_id = u.id
        WHERE LOWER(r.depart) = LOWER(?) AND LOWER(r.destination) = LOWER(?) AND r.jour = ?
    ''', (depart, destination, jour))

    results = cursor.fetchall()
    conn.close()

    if results:
        trajets = []
        for row in results:
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
    else:
        return jsonify({'message': 'Aucun trajet trouvé'}), 404

# ----------- INIT DB + RUN ------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    