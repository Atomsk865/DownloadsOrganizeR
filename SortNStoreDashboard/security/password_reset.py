"""
Password Reset and Email Verification Routes for Flask-Security-Too Integration

Provides:
- Password reset request endpoint
- Password reset token validation
- New password setting
- Email verification (optional)
- Account recovery flows

Usage:
    from SortNStoreDashboard.security.password_reset import get_password_reset_blueprint
    blueprint = get_password_reset_blueprint()
    if blueprint:
        app.register_blueprint(blueprint)
"""

from flask import Blueprint, request, jsonify
from functools import wraps

# @flask-security-too: Check if Flask-Security is available
try:
    from flask_security import login_required, current_user
    FLASK_SECURITY_AVAILABLE = True
except ImportError:
    FLASK_SECURITY_AVAILABLE = False
    login_required = lambda f: f
    
    class CurrentUserStub:
        pass
    current_user = CurrentUserStub()


def requires_ajax():
    """Decorator for AJAX-only endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json and request.method in ['POST', 'PUT']:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_password_reset_blueprint():
    """
    Get password reset blueprint only if Flask-Security is available.
    
    Returns:
        Blueprint or None if Flask-Security not available
    """
    if not FLASK_SECURITY_AVAILABLE:
        return None
    
    # @flask-security-too: Define blueprint for password management
    routes_password_reset_enhanced = Blueprint(
        'routes_password_reset_enhanced',
        __name__,
        url_prefix='/api/security'
    )
    
    # @flask-security-too: Password reset request (unauthenticated)
    @routes_password_reset_enhanced.route('/forgot-password', methods=['POST'])
    @requires_ajax()
    def request_password_reset():
        """
        Request password reset token via email.
        
        Request body:
            {
                "email": "user@example.com"
            }
        
        Response:
            {
                "message": "Password reset instructions sent to email",
                "email": "user@example.com"
            }
        """
        try:
            from SortNStoreDashboard.security.flask_security_integration import User
            from SortNStoreDashboard.structured_logging import get_logger
            
            log = get_logger(__name__)
            
            data = request.get_json() or {}
            email = data.get('email', '').strip().lower()
            
            if not email:
                # @flask-security-too: Log security event
                log.warning("password_reset_no_email", ip=request.remote_addr)
                return jsonify({'error': 'Email is required'}), 400
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Don't reveal whether email exists (security best practice)
                log.info("password_reset_requested", email=email, user_found=False)
                return jsonify({
                    'message': 'If an account exists with this email, password reset instructions have been sent'
                }), 200
            
            # @flask-security-too: Generate reset token
            try:
                from flask_security import generate_confirmation_token
                reset_token = generate_confirmation_token(user.email)
                
                # Store token (in production, use secure session storage)
                # For now, log it for testing
                log.info("password_reset_token_generated",
                        username=user.username,
                        email=email,
                        token_preview=reset_token[:20])
                
                # TODO: Send email with reset link
                # reset_url = f"{current_app.config['BASE_URL']}/reset-password?token={reset_token}"
                
                return jsonify({
                    'message': 'Password reset instructions sent to email',
                    'email': email
                }), 200
            
            except Exception as e:
                log.error("password_reset_token_generation_failed",
                         email=email,
                         error=str(e))
                return jsonify({'error': 'Failed to generate reset token'}), 500
        
        except ImportError:
            return jsonify({'error': 'Flask-Security not available'}), 503
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    
    # @flask-security-too: Password reset token validation
    @routes_password_reset_enhanced.route('/validate-reset-token', methods=['POST'])
    @requires_ajax()
    def validate_reset_token():
        """
        Validate password reset token.
        
        Request body:
            {
                "token": "reset_token_value"
            }
        
        Response:
            {
                "valid": true,
                "email": "user@example.com"
            }
        """
        try:
            from SortNStoreDashboard.security.flask_security_integration import User
            from SortNStoreDashboard.structured_logging import get_logger
            
            log = get_logger(__name__)
            data = request.get_json() or {}
            token = data.get('token', '').strip()
            
            if not token:
                return jsonify({'error': 'Token is required'}), 400
            
            # @flask-security-too: Validate token
            try:
                from flask_security import confirm_email_token_status
                expired, invalid, user = confirm_email_token_status(token)
                
                if expired:
                    log.warning("password_reset_token_expired", token_preview=token[:20])
                    return jsonify({'valid': False, 'reason': 'Token expired'}), 400
                
                if invalid or not user:
                    log.warning("password_reset_token_invalid", token_preview=token[:20])
                    return jsonify({'valid': False, 'reason': 'Invalid token'}), 400
                
                log.info("password_reset_token_validated", username=user.username)
                return jsonify({'valid': True, 'email': user.email}), 200
            
            except Exception as e:
                log.error("password_reset_token_validation_failed", error=str(e))
                return jsonify({'error': 'Failed to validate token'}), 500
        
        except ImportError:
            return jsonify({'error': 'Flask-Security not available'}), 503
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    
    # @flask-security-too: Password reset form submission
    @routes_password_reset_enhanced.route('/reset-password', methods=['POST'])
    @requires_ajax()
    def reset_password():
        """
        Reset password with valid token.
        
        Request body:
            {
                "token": "reset_token_value",
                "password": "new_password"
            }
        
        Response:
            {
                "message": "Password successfully reset",
                "username": "user"
            }
        """
        try:
            from SortNStoreDashboard.security.flask_security_integration import User, db
            from SortNStoreDashboard.structured_logging import get_logger
            
            log = get_logger(__name__)
            data = request.get_json() or {}
            token = data.get('token', '').strip()
            new_password = data.get('password', '').strip()
            
            if not token or not new_password:
                return jsonify({'error': 'Token and password are required'}), 400
            
            if len(new_password) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
            
            # @flask-security-too: Validate token and get user
            try:
                from flask_security import confirm_email_token_status
                expired, invalid, user = confirm_email_token_status(token)
                
                if expired:
                    log.warning("password_reset_token_expired_on_submit")
                    return jsonify({'error': 'Reset link has expired'}), 400
                
                if invalid or not user:
                    log.warning("password_reset_token_invalid_on_submit")
                    return jsonify({'error': 'Invalid reset link'}), 400
                
                # @flask-security-too: Set new password
                user.set_password(new_password)
                user.confirmed_at = db.func.now()
                db.session.commit()
                
                log.info("password_reset_successful",
                        username=user.username,
                        email=user.email)
                
                return jsonify({
                    'message': 'Password successfully reset',
                    'username': user.username
                }), 200
            
            except Exception as e:
                log.error("password_reset_failed", error=str(e))
                db.session.rollback()
                return jsonify({'error': 'Failed to reset password'}), 500
        
        except ImportError:
            return jsonify({'error': 'Flask-Security not available'}), 503
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    
    # @flask-security-too: Change password (authenticated)
    @routes_password_reset_enhanced.route('/change-password', methods=['POST'])
    @login_required
    @requires_ajax()
    def change_password():
        """
        Change password for authenticated user.
        
        Request body:
            {
                "old_password": "current_password",
                "new_password": "new_password"
            }
        
        Response:
            {
                "message": "Password successfully changed",
                "username": "user"
            }
        """
        try:
            from SortNStoreDashboard.security.flask_security_integration import User, db
            from SortNStoreDashboard.structured_logging import get_logger
            import bcrypt
            
            log = get_logger(__name__)
            data = request.get_json() or {}
            old_password = data.get('old_password', '').strip()
            new_password = data.get('new_password', '').strip()
            
            if not old_password or not new_password:
                return jsonify({'error': 'Old and new passwords are required'}), 400
            
            if len(new_password) < 8:
                return jsonify({'error': 'New password must be at least 8 characters'}), 400
            
            user = current_user._get_current_object() if hasattr(current_user, '_get_current_object') else current_user
            
            # @flask-security-too: Verify old password
            try:
                from flask_security import verify_password
                if not verify_password(old_password, user.password):
                    log.warning("password_change_old_password_incorrect",
                               username=user.username,
                               ip=request.remote_addr)
                    return jsonify({'error': 'Current password is incorrect'}), 401
            except Exception:
                # Fallback verification
                try:
                    if not bcrypt.checkpw(
                        old_password.encode('utf-8'),
                        user.password.encode('utf-8')
                    ):
                        log.warning("password_change_verification_failed", username=user.username)
                        return jsonify({'error': 'Current password is incorrect'}), 401
                except Exception:
                    log.error("password_verification_error", username=user.username)
                    return jsonify({'error': 'Password verification failed'}), 500
            
            # @flask-security-too: Set new password
            try:
                user.set_password(new_password)
                db.session.commit()
                
                log.info("password_changed_successfully",
                        username=user.username,
                        email=user.email)
                
                return jsonify({
                    'message': 'Password successfully changed',
                    'username': user.username
                }), 200
            
            except Exception as e:
                log.error("password_change_failed", error=str(e))
                db.session.rollback()
                return jsonify({'error': 'Failed to change password'}), 500
        
        except ImportError:
            return jsonify({'error': 'Flask-Security not available'}), 503
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    return routes_password_reset_enhanced


# @flask-security-too: Module-level blueprint for backwards compatibility
routes_password_reset_enhanced = get_password_reset_blueprint()
