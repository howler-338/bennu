from datetime import datetime, timedelta, timezone

from celery import shared_task

from app.documents.models import Document, DocumentStatus
from app.embeddings.models import DocumentChunk
from app.extensions import db
from app.services.chunker import chunk_text
from app.services.embedder import embed_text
from app.services.text_extractor import extract_text


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id: str):
    document = db.session.get(Document, document_id)
    if not document:
        return

    try:
        document.status = DocumentStatus.PROCESSING
        db.session.commit()

        text = extract_text(document.file_path, document.mime_type)
        chunks = chunk_text(text)

        db.session.execute(db.delete(DocumentChunk).where(DocumentChunk.document_id == document.id))

        for i, content in enumerate(chunks):
            embedding = embed_text(content)
            db.session.add(DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=content,
                embedding=embedding,
            ))

        document.status = DocumentStatus.READY
        db.session.commit()

    except Exception as exc:
        db.session.rollback()
        try:
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        except Exception:
            doc = db.session.get(Document, document_id)
            if doc:
                doc.status = DocumentStatus.FAILED
                db.session.commit()
            raise


@shared_task
def retry_stuck_documents():
    """Re-queue documents stuck in PROCESSING for more than 10 minutes."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    stuck = Document.query.filter(
        Document.status == DocumentStatus.PROCESSING,
        Document.updated_at < cutoff,
    ).all()
    for doc in stuck:
        doc.status = DocumentStatus.PENDING
        db.session.commit()
        process_document.delay(str(doc.id))
    return len(stuck)
