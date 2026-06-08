"""
Authentication routes
Handles user signup, login, logout, password reset, email verification
"""

from flask import Blueprint, request, jsonify, current_app
from models.models import db, User, UserRole
from utils.auth import (
    generate_token, verify_token, token_required, 
    generate_email_token, verify_email_token,
    generate_password_reset_token, verify_password_reset_token
)
from utils.email import send_verification_email, send_password_reset_email, send_welcome_email
from utils.security import validate_email, validate_password, sanitize_input, rate_limit
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
@rate_limit("10 per hour")
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Sanitize inputs
        username = sanitize_input(data['username']).strip()
        email = sanitize_input(data['email']).strip().lower()
        password = data['password']
        first_name = sanitize_input(data['first_name']).strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 409
        
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already taken'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=data.get('last_name', ''),
            role=UserRole.USER
        )
        user.set_password(password)
        
        # Generate verification token
        verification_token = user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(email, verification_token)
        
        return jsonify({
            'message': 'User registered successfully. Please check your email to verify.',
            'user_id': user.id,
            'email': email
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit("5 per minute")
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        email = sanitize_input(data['email']).strip().lower()
        password = data['password']
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is disabled'}), 403
        
        if not user.is_verified:
            return jsonify({'message': 'Please verify your email first'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate tokens
        access_token = generate_token(user.id, 'access')
        refresh_token = generate_token(user.id, 'refresh')
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'role': user.role.value
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout"""
    # Token is invalidated on frontend by removing it
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email"""
    try:
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({'message': 'Invalid verification link'}), 400
        
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(user.email, user.first_name)
        
        return jsonify({'message': 'Email verified successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
@rate_limit("3 per hour")
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
        
        email = sanitize_input(data['email']).strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = generate_password_reset_token(email)
            send_password_reset_email(email, reset_token)
        
        # Don't reveal if user exists
        return jsonify({'message': 'If email exists, password reset link has been sent'}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset user password"""
    try:
        data = request.get_json()
        
        if not data.get('password'):
            return jsonify({'message': 'New password is required'}), 400
        
        email = verify_password_reset_token(token)
        
        if not email:
            return jsonify({'message': 'Invalid or expired reset link'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Validate new password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'message': message}), 400
        
        user.set_password(data['password'])
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """Get new access token using refresh token"""
    try:
        data = request.get_json()
        
        if not data.get('refresh_token'):
            return jsonify({'message': 'Refresh token is required'}), 400
        
        payload = verify_token(data['refresh_token'], 'refresh')
        
        if not payload:
            return jsonify({'message': 'Invalid refresh token'}), 401
        
        user_id = payload['user_id']
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'User not found or inactive'}), 404
        
        new_access_token = generate_token(user_id, 'access')
        
        return jsonify({
            'access_token': new_access_token
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    try:
        user = User.query.get(request.user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'bio': user.bio,
                'profile_picture': user.profile_picture,
                'role': user.role.value,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
