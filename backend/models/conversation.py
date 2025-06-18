import sqlite3
from backend.database.connection import get_connection

def get_or_create_conversation(user1_id, user2_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Vérifie si la conversation existe (dans un ordre ou dans l'autre)
    cursor.execute('''
        SELECT * FROM conversations
        WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
    ''', (user1_id, user2_id, user2_id, user1_id))
    conversation = cursor.fetchone()

    if conversation:
        conn.close()
        return conversation['id']

    # Sinon on la crée
    cursor.execute('''
        INSERT INTO conversations (user1_id, user2_id)
        VALUES (?, ?)
    ''', (user1_id, user2_id))
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return conversation_id