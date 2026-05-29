from functools import wraps

from flask import abort
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.auth.models import User, UserRole


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = db_get_user(get_jwt_identity())
        if not user or user.role != UserRole.ADMIN:
            abort(403, description="Admin access required")
        return fn(*args, **kwargs)
    return wrapper


def db_get_user(user_id):
    from app.extensions import db
    return db.session.get(User, user_id)
