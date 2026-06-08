"""
Messaging routes
Handles message sending and retrieval
"""

from flask import Blueprint, request, jsonify
from models.models import db, Message, User, Notification
from utils.auth import token_required
from utils.security import sanitize_input
from utils.email import send_new_message_notification
from datetime import datetime

message_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


@message_bp.route('/', methods=['GET'])
@token_required
def get_messages():
    """Get user messages"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get both sent and received messages
        received = Message.query.filter_by(receiver_id=request.user_id).order_by(Message.created_at.desc())
        sent = Message.query.filter_by(sender_id=request.user_id).order_by(Message.created_at.desc())
        
        received_paginated = received.paginate(page=page, per_page=per_page, error_out=False)
        
        messages = []
        for msg in received_paginated.items:
            messages.append({
                'id': msg.id,
                'from': f"{msg.sender.first_name} {msg.sender.last_name}",
                'to': f"{msg.receiver.first_name} {msg.receiver.last_name}",
                'content': msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.isoformat(),
                'read_at': msg.read_at.isoformat() if msg.read_at else None
            })
        
        return jsonify({
            'data': messages,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': received_paginated.total,
                'pages': received_paginated.pages
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@message_bp.route('/conversation/<int:user_id>', methods=['GET'])
@token_required
def get_conversation(user_id):
    """Get conversation with a specific user"""
    try:
        # Get all messages between two users
        messages = Message.query.filter(
            ((Message.sender_id == request.user_id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == request.user_id))
        ).order_by(Message.created_at.asc()).all()
        
        # Mark messages as read
        for msg in messages:
            if msg.receiver_id == request.user_id and not msg.is_read:
                msg.is_read = True
                msg.read_at = datetime.utcnow()
        
        db.session.commit()
        
        conversation = [{
            'id': msg.id,
            'sender_id': msg.sender_id,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'is_read': msg.is_read
        } for msg in messages]
        
        return jsonify({'data': conversation}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@message_bp.route('/send/<int:receiver_id>', methods=['POST'])
@token_required
def send_message(receiver_id):
    """Send message to another user"""
    try:
        receiver = User.query.get(receiver_id)
        
        if not receiver:
            return jsonify({'message': 'Recipient not found'}), 404
        
        if receiver_id == request.user_id:
            return jsonify({'message': 'Cannot send message to yourself'}), 400
        
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'message': 'Message content is required'}), 400
        
        content = sanitize_input(data['content'])
        
        message = Message(
            sender_id=request.user_id,
            receiver_id=receiver_id,
            content=content
        )
        
        db.session.add(message)
        db.session.flush()
        
        # Create notification
        notification = Notification(
            user_id=receiver_id,
            title='New Message',
            message=f"You have a new message from {User.query.get(request.user_id).first_name}",
            notification_type='message',
            related_id=message.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Send email notification
        send_new_message_notification(receiver.email, User.query.get(request.user_id).first_name)
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@message_bp.route('/<int:message_id>/mark-read', methods=['PUT'])
@token_required
def mark_message_read(message_id):
    """Mark message as read"""
    try:
        message = Message.query.get(message_id)
        
        if not message:
            return jsonify({'message': 'Message not found'}), 404
        
        if message.receiver_id != request.user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Message marked as read'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
