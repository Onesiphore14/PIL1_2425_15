from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.conversation import Conversation
from models.message import Message
from app import db, socketio
from flask_socketio import emit

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = get_jwt_identity()
    
    conversations = db.session.query(Conversation).filter(
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
    ).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        # Obtenir le dernier message
        last_message = Message.query.filter_by(
            conversation_id=conv.id
        ).order_by(Message.created_at.desc()).first()
        
        # Déterminer l'autre utilisateur
        other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
        
        # Compter les messages non lus
        unread_count = Message.query.filter(
            Message.conversation_id == conv.id,
            Message.sender_id != user_id,
            Message.is_read == False
        ).count()
        
        conv_data = conv.to_dict()
        conv_data['other_user_id'] = other_user_id
        conv_data['last_message'] = last_message.to_dict() if last_message else None
        conv_data['unread_count'] = unread_count
        
        result.append(conv_data)
    
    return jsonify(result)

@messaging_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    user_id = get_jwt_identity()
    
    # Vérifier que l'utilisateur fait partie de la conversation
    conversation = Conversation.query.filter(
        Conversation.id == conversation_id,
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation non trouvée'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = Message.query.filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Marquer les messages comme lus
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,
        Message.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify({
        'messages': [message.to_dict() for message in messages.items],
        'total': messages.total,
        'pages': messages.pages,
        'current_page': page
    })

@messaging_bp.route('/conversations/start', methods=['POST'])
@jwt_required()
def start_conversation():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({'error': 'ID utilisateur requis'}), 400
    
    other_user_id = data['user_id']
    
    if user_id == other_user_id:
        return jsonify({'error': 'Impossible de créer une conversation avec soi-même'}), 400
    
    conversation = Conversation.get_or_create_conversation(user_id, other_user_id)
    
    return jsonify(conversation.to_dict())

@messaging_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'conversation_id' not in data or 'content' not in data:
        return jsonify({'error': 'Données incomplètes'}), 400
    
    conversation_id = data['conversation_id']
    content = data['content'].strip()
    
    if not content:
        return jsonify({'error': 'Le message ne peut pas être vide'}), 400
    
    # Vérifier que l'utilisateur fait partie de la conversation
    conversation = Conversation.query.filter(
        Conversation.id == conversation_id,
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
    ).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation non trouvée'}), 404
    
    # Créer le message
    message = Message(
        conversation_id=conversation_id,
        sender_id=user_id,
        content=content
    )
    
    db.session.add(message)
    
    # Mettre à jour la conversation
    conversation.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Émettre le message via Socket.IO
    socketio.emit('new_message', {
        'message': message.to_dict(),
        'conversation_id': conversation_id
    }, room=f'conversation_{conversation_id}')
    
    return jsonify(message.to_dict())
