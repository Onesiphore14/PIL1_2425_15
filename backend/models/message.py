from backend.database.connection import get_connection

def send_message(conversation_id, sender_id, contenu):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (conversation_id, sender_id, contenu)
        VALUES (?, ?, ?)
    ''', (conversation_id, sender_id, contenu))
    conn.commit()
    conn.close()


def get_messages(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.*, u.nom, u.prenom FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
    ''', (conversation_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages