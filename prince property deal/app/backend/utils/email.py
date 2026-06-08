"""
Email utilities
Handles sending emails for verification, notifications, etc.
"""

from flask import render_template, current_app
from flask_mail import Mail, Message
import os


mail = Mail()


def send_verification_email(user_email, token):
    """Send email verification message"""
    verification_link = f"{current_app.config.get('APP_URL', 'http://localhost:5000')}/verify-email/{token}"
    
    msg = Message(
        subject='Verify Your Email Address',
        recipients=[user_email],
        html=f"""
        <html>
            <body>
                <h2>Welcome to Prince Properties!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>This link expires in 1 hour.</p>
                <p>If you did not create this account, please ignore this email.</p>
            </body>
        </html>
        """
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_password_reset_email(user_email, token):
    """Send password reset email"""
    reset_link = f"{current_app.config.get('APP_URL', 'http://localhost:5000')}/reset-password/{token}"
    
    msg = Message(
        subject='Reset Your Password',
        recipients=[user_email],
        html=f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>We received a request to reset your password. Click the link below:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link expires in 1 hour.</p>
                <p>If you did not request this, please ignore this email.</p>
            </body>
        </html>
        """
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_welcome_email(user_email, user_name):
    """Send welcome email to new user"""
    msg = Message(
        subject='Welcome to Prince Properties!',
        recipients=[user_email],
        html=f"""
        <html>
            <body>
                <h2>Welcome, {user_name}!</h2>
                <p>Your account has been created successfully.</p>
                <p>You can now:</p>
                <ul>
                    <li>Browse our property listings</li>
                    <li>Create your profile</li>
                    <li>Save favorite properties</li>
                    <li>Contact property owners</li>
                </ul>
                <p>Happy browsing!</p>
            </body>
        </html>
        """
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_inquiry_confirmation(user_email, property_title, inquiry_id):
    """Send inquiry confirmation email"""
    msg = Message(
        subject='Your Property Inquiry Has Been Received',
        recipients=[user_email],
        html=f"""
        <html>
            <body>
                <h2>Inquiry Confirmation</h2>
                <p>Thank you for your interest in "{property_title}".</p>
                <p>Your inquiry reference number is: {inquiry_id}</p>
                <p>The property owner will contact you shortly.</p>
            </body>
        </html>
        """
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_new_message_notification(recipient_email, sender_name):
    """Send notification for new message"""
    msg = Message(
        subject=f'New Message from {sender_name}',
        recipients=[recipient_email],
        html=f"""
        <html>
            <body>
                <h2>New Message</h2>
                <p>You have received a new message from {sender_name}.</p>
                <p>Log in to your account to read the message.</p>
            </body>
        </html>
        """
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
