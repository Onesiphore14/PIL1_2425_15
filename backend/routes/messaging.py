from flask import Blueprint, request, jsonify
from backend.models.conversation import get_or_create_conversation
from backend.models.message import send_message, get_messages
from backend.database.connection import get_connection

messaging_routes = Blueprint('messaging', __name__)

#envoy de message
@messaging_routes.route('/messages/send', methods=['POST'])
def envoyer_message():
    sender_id = request.form.get('sender_id')
    receiver_id = request.form.get('receiver_id')
    contenu = request.form.get('contenu')

    if not all([sender_id, receiver_id, contenu]):
        return jsonify({'error': 'Champs requis'}), 400

    conversation_id = get_or_create_conversation(sender_id, receiver_id)
    send_message(conversation_id, sender_id, contenu)
    return jsonify({'message': 'Message envoyé'}), 200

#lire les messages
@messaging_routes.route('/messages/<int:user1_id>/<int:user2_id>', methods=['GET'])
def lire_messages(user1_id, user2_id):
    conversation_id = get_or_create_conversation(user1_id, user2_id)
    messages = get_messages(conversation_id)
    return jsonify([{
        'nom': m['nom'],
        'prenom': m['prenom'],
        'contenu': m['contenu'],
        'timestamp': m['timestamp']
    } for m in messages])

#route pour lister des conversation
@messaging_routes.route('/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.id AS conversation_id, u.id AS user_id, u.nom, u.prenom
        FROM conversations c
        JOIN users u ON (u.id = CASE
            WHEN c.user1_id = ? THEN c.user2_id
            ELSE c.user1_id
        END)
        WHERE c.user1_id = ? OR c.user2_id = ?
    ''', (user_id, user_id, user_id))

    conversations = cursor.fetchall()
    conn.close()

    return jsonify([{
        'conversation_id': conv['conversation_id'],
        'user_id': conv['user_id'],
        'nom': conv['nom'],
        'prenom': conv['prenom']
    } for conv in conversations])

#route pour rechercher des utilisateur
@messaging_routes.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('query')
    if not query:
        return jsonify([])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nom, prenom, email FROM users
        WHERE LOWER(nom) LIKE ? OR LOWER(prenom) LIKE ? OR LOWER(email) LIKE ?
    ''', (f'%{query.lower()}%', f'%{query.lower()}%', f'%{query.lower()}%'))

    results = cursor.fetchall()
    conn.close()

    return jsonify([{
        'id': u['id'],
        'nom': u['nom'],
        'prenom': u['prenom'],
        'email': u['email']
    } for u in results])
