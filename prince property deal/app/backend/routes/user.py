"""
User routes
Handles user profiles and user management
"""

from flask import Blueprint, request, jsonify
from models.models import db, User, Property
from utils.auth import token_required
from utils.security import sanitize_input
from datetime import datetime

user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@user_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get user properties count
        properties_count = Property.query.filter_by(owner_id=user_id).count()
        
        profile_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'bio': user.bio,
            'profile_picture': user.profile_picture,
            'role': user.role.value,
            'properties_count': properties_count,
            'member_since': user.created_at.isoformat(),
            'is_verified': user.is_verified
        }
        
        return jsonify({'data': profile_data}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'first_name' in data:
            user.first_name = sanitize_input(data['first_name'])
        
        if 'last_name' in data:
            user.last_name = sanitize_input(data['last_name'])
        
        if 'phone' in data:
            user.phone = sanitize_input(data['phone'])
        
        if 'bio' in data:
            user.bio = sanitize_input(data['bio'])
        
        if 'profile_picture' in data:
            user.profile_picture = sanitize_input(data['profile_picture'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@user_bp.route('/properties', methods=['GET'])
@token_required
def get_user_properties():
    """Get current user's properties"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Property.query.filter_by(owner_id=request.user_id)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        properties = [{
            'id': prop.id,
            'title': prop.title,
            'price': prop.price,
            'address': prop.address,
            'views': prop.views,
            'status': prop.status.value,
            'created_at': prop.created_at.isoformat()
        } for prop in pagination.items]
        
        return jsonify({
            'data': properties,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/<int:user_id>/properties', methods=['GET'])
def get_user_public_properties(user_id):
    """Get public properties of a user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        query = Property.query.filter_by(owner_id=user_id)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        properties = [{
            'id': prop.id,
            'title': prop.title,
            'price': prop.price,
            'address': prop.address,
            'main_image': prop.main_image,
            'views': prop.views
        } for prop in pagination.items]
        
        return jsonify({'data': properties}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'Current and new password required'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'message': 'Current password is incorrect'}), 401
        
        from utils.security import validate_password
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
