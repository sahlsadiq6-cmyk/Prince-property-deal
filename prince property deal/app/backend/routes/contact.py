"""
Contact routes
Handles contact form submissions
"""

from flask import Blueprint, request, jsonify
from models.models import db, Contact
from utils.security import sanitize_input, validate_email, rate_limit
from utils.database import track_event

contact_bp = Blueprint('contact', __name__, url_prefix='/api/contact')


@contact_bp.route('/', methods=['POST'])
@rate_limit("5 per hour")
def submit_contact_form():
    """Submit contact form"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate email
        email = sanitize_input(data['email']).strip().lower()
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        contact = Contact(
            name=sanitize_input(data['name']),
            email=email,
            phone=sanitize_input(data.get('phone', '')),
            subject=sanitize_input(data['subject']),
            message=sanitize_input(data['message'])
        )
        
        db.session.add(contact)
        db.session.commit()
        
        track_event('contact_form_submitted', {
            'subject': data['subject'],
            'email': email
        })
        
        return jsonify({
            'message': 'Your message has been received. We will contact you soon.',
            'contact_id': contact.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
