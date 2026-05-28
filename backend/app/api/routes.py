"""Top-level API blueprint."""

from flask import Blueprint

from app.auth.routes import auth_bp
from app.chat.routes import chat_bp
from app.documents.routes import documents_bp
from app.embeddings.routes import embeddings_bp
from app.rag.routes import rag_bp

api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(auth_bp, url_prefix="/auth")
api_bp.register_blueprint(documents_bp, url_prefix="/documents")
api_bp.register_blueprint(embeddings_bp, url_prefix="/embeddings")
api_bp.register_blueprint(rag_bp, url_prefix="/rag")
api_bp.register_blueprint(chat_bp, url_prefix="/chat")
