from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_smorest import Blueprint, abort

from app.auth.models import User
from app.auth.schemas import (
    AccessTokenSchema,
    AuthMessageSchema,
    LoginSchema,
    RegisterSchema,
    TokenSchema,
    UserSchema,
)
from app.extensions import db, limiter

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth", description="Authentication")


@auth_bp.post("/register")
@limiter.limit("5 per minute")
@auth_bp.arguments(RegisterSchema)
@auth_bp.response(201, TokenSchema)
def register(data):
    email = data["email"].strip().lower()

    if User.query.filter_by(email=email).first():
        abort(409, message="Email already registered")

    user = User(email=email)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return {
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
        "user": user,
    }


@auth_bp.post("/login")
@limiter.limit("10 per minute")
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, TokenSchema)
def login(data):
    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(data["password"]):
        abort(401, message="Invalid email or password")

    if not user.is_active:
        abort(403, message="Account is inactive")

    return {
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
        "user": user,
    }


@auth_bp.post("/logout")
@jwt_required()
@auth_bp.response(200, AuthMessageSchema)
def logout():
    return {"message": "Logged out successfully"}


@auth_bp.get("/me")
@jwt_required()
@auth_bp.response(200, UserSchema)
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        abort(404, message="User not found")

    return user


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@auth_bp.response(200, AccessTokenSchema)
def refresh():
    return {"access_token": create_access_token(identity=get_jwt_identity())}
