"""Authentication API routes."""

from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    """Register a new user."""
    return jsonify({"message": "Not implemented"}), 501


@auth_bp.post("/login")
def login():
    """Authenticate and return tokens."""
    return jsonify({"message": "Not implemented"}), 501


@auth_bp.post("/logout")
def logout():
    """Invalidate session / refresh token."""
    return jsonify({"message": "Not implemented"}), 501
