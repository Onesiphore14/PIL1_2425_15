from flask import Blueprint, request, jsonify
from backend.database.connection import get_connection

rides_routes = Blueprint("rides", __name__)

@rides_routes.route("/rides/add", methods=["POST"])
def ajouter_ride():
    user_id = request.form.get("user_id")
    type_publication = request.form.get("postType")
    depart = request.form.get("depart")
    destination = request.form.get("destination")
    heure = request.form.get("heure")
    places = request.form.get("places")
    commentaires = request.form.get("commentaires")

    if not all([user_id, type_publication, depart, destination]):
        return "Champs obligatoires manquants", 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO rides (user_id, type, depart, destination, heure, places_disponibles, commentaires)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, type_publication, depart, destination, heure, places, commentaires))
    conn.commit()
    conn.close()

    return "Trajet publié avec succès ✅", 200

@rides_routes.route('/rides/all', methods=['GET'])
def lister_rides():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.*, u.nom, u.prenom
        FROM rides r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.id DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    return jsonify([{
        'id': r['id'],
        'user_id': r['user_id'],
        'type': r['type'],
        'depart': r['depart'],
        'destination': r['destination'],
        'heure': r['heure'],
        'places_disponibles': r['places_disponibles'],
        'commentaires': r['commentaires'],
        'nom': r['nom'],
        'prenom': r['prenom']
    } for r in rows])
