from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from app import socketio
import jwt

connected_users = {}

@socketio.on('connect')
def handle_connect(auth):
    try:
        token = auth['token'] if auth else None
        if not token:
            disconnect()
            return
        
        # Décoder le token JWT
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        
        connected_users[request.sid] = user_id
        emit('connected', {'status': 'Connecté'})
        
    except Exception as e:
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_users:
        del connected_users[request.sid]

@socketio.on('join_conversation')
def handle_join_conversation(data):
    if request.sid in connected_users:
        conversation_id = data['conversation_id']
        join_room(f'conversation_{conversation_id}')
        emit('joined_conversation', {'conversation_id': conversation_id})

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    if request.sid in connected_users:
        conversation_id = data['conversation_id']
        leave_room(f'conversation_{conversation_id}')
        emit('left_conversation', {'conversation_id': conversation_id})

@socketio.on('typing')
def handle_typing(data):
    if request.sid in connected_users:
        user_id = connected_users[request.sid]
        conversation_id = data['conversation_id']
        
        emit('user_typing', {
            'user_id': user_id,
            'conversation_id': conversation_id
        }, room=f'conversation_{conversation_id}', include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    if request.sid in connected_users:
        user_id = connected_users[request.sid]
        conversation_id = data['conversation_id']
        
        emit('user_stop_typing', {
            'user_id': user_id,
            'conversation_id': conversation_id
        }, room=f'conversation_{conversation_id}', include_self=False)