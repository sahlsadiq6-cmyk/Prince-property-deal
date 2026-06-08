"""
Admin routes
Handles admin functionalities
"""

from flask import Blueprint, request, jsonify
from models.models import db, User, Property, Contact, Inquiry, Analytics
from utils.auth import admin_required
from utils.database import paginate_query, get_analytics_summary

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get admin dashboard statistics"""
    try:
        total_users = User.query.count()
        total_properties = Property.query.count()
        total_contacts = Contact.query.count()
        pending_inquiries = Inquiry.query.filter_by(status='pending').count()
        
        analytics = get_analytics_summary(days=30)
        
        return jsonify({
            'statistics': {
                'total_users': total_users,
                'total_properties': total_properties,
                'total_contacts': total_contacts,
                'pending_inquiries': pending_inquiries
            },
            'analytics': analytics
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = User.query
        result = paginate_query(query, page, per_page)
        
        users = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat()
        } for user in result['items']]
        
        return jsonify({
            'data': users,
            'pagination': {
                'current_page': result['current_page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/contacts', methods=['GET'])
@admin_required
def get_all_contacts():
    """Get all contact submissions"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Contact.query.order_by(Contact.created_at.desc())
        result = paginate_query(query, page, per_page)
        
        contacts = [{
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'subject': contact.subject,
            'message': contact.message,
            'is_replied': contact.is_replied,
            'created_at': contact.created_at.isoformat()
        } for contact in result['items']]
        
        return jsonify({
            'data': contacts,
            'pagination': {
                'current_page': result['current_page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/contacts/<int:contact_id>/reply', methods=['POST'])
@admin_required
def reply_contact(contact_id):
    """Mark contact as replied"""
    try:
        contact = Contact.query.get(contact_id)
        
        if not contact:
            return jsonify({'message': 'Contact not found'}), 404
        
        data = request.get_json()
        
        contact.is_replied = True
        contact.admin_notes = data.get('notes', '')
        db.session.commit()
        
        return jsonify({'message': 'Contact marked as replied'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/inquiries', methods=['GET'])
@admin_required
def get_inquiries():
    """Get property inquiries"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Inquiry.query
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Inquiry.created_at.desc())
        result = paginate_query(query, page, per_page)
        
        inquiries = [{
            'id': inquiry.id,
            'property': inquiry.property.title,
            'name': inquiry.name,
            'email': inquiry.email,
            'phone': inquiry.phone,
            'message': inquiry.message,
            'status': inquiry.status,
            'created_at': inquiry.created_at.isoformat()
        } for inquiry in result['items']]
        
        return jsonify({
            'data': inquiries,
            'pagination': {
                'current_page': result['current_page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/properties', methods=['GET'])
@admin_required
def get_all_properties():
    """Get all properties for admin"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Property.query
        result = paginate_query(query, page, per_page)
        
        properties = [{
            'id': prop.id,
            'title': prop.title,
            'price': prop.price,
            'owner': prop.owner.username,
            'status': prop.status.value,
            'views': prop.views,
            'created_at': prop.created_at.isoformat()
        } for prop in result['items']]
        
        return jsonify({
            'data': properties,
            'pagination': {
                'current_page': result['current_page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/properties/<int:property_id>/feature', methods=['PUT'])
@admin_required
def feature_property(property_id):
    """Feature/unfeature a property"""
    try:
        property_obj = Property.query.get(property_id)
        
        if not property_obj:
            return jsonify({'message': 'Property not found'}), 404
        
        data = request.get_json()
        property_obj.is_featured = data.get('is_featured', False)
        db.session.commit()
        
        return jsonify({'message': 'Property updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
