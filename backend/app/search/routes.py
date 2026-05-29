from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from app.documents.models import Document, DocumentStatus
from app.embeddings.models import DocumentChunk
from app.extensions import db
from app.search.schemas import SearchQuerySchema, SearchResultsSchema
from app.services.embedder import embed_text

search_bp = Blueprint("search", __name__, url_prefix="/api/search", description="Semantic search")


@search_bp.post("")
@jwt_required()
@search_bp.arguments(SearchQuerySchema)
@search_bp.response(200, SearchResultsSchema)
def search(args):
    user_id = get_jwt_identity()
    query_embedding = embed_text(args["query"])

    rows = (
        db.session.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .filter(Document.status == DocumentStatus.READY)
        .order_by("distance")
        .limit(args["limit"])
        .all()
    )

    return {
        "results": [
            {
                "content": chunk.content,
                "similarity": round(1 - distance, 4),
                "chunk_index": chunk.chunk_index,
                "document": chunk.document,
            }
            for chunk, distance in rows
        ]
    }
