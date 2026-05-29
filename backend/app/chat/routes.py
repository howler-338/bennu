from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint

from app.chat.schemas import ChatQuerySchema, ChatResponseSchema
from app.documents.models import Document, DocumentStatus
from app.embeddings.models import DocumentChunk
from app.extensions import db
from app.services.embedder import embed_text
from app.services.llm import chat as llm_chat

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat", description="RAG chat")

_SYSTEM_PROMPT_WITH_CONTEXT = """You are a helpful assistant. Answer the user's question using only the context below.
If the context doesn't contain enough information to answer clearly, say so.

Context:
{context}"""

_SYSTEM_PROMPT_NO_CONTEXT = "You are a helpful assistant. Answer the user's question as best you can."


@chat_bp.post("")
@jwt_required()
@chat_bp.arguments(ChatQuerySchema)
@chat_bp.response(200, ChatResponseSchema)
def chat(args):
    user_id = get_jwt_identity()

    query_embedding = embed_text(args["message"])

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

    if rows:
        context = "\n---\n".join(chunk.content for chunk, _ in rows)
        system = _SYSTEM_PROMPT_WITH_CONTEXT.format(context=context)
    else:
        system = _SYSTEM_PROMPT_NO_CONTEXT

    messages = (
        [{"role": "system", "content": system}]
        + args["history"]
        + [{"role": "user", "content": args["message"]}]
    )

    reply = llm_chat(messages)

    sources = [
        {
            "document_id": str(chunk.document_id),
            "filename": chunk.document.original_filename,
            "chunk_index": chunk.chunk_index,
        }
        for chunk, _ in rows
    ]

    return {"reply": reply, "sources": sources}
