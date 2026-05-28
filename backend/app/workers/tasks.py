"""Celery task definitions for document processing."""

from app.workers.celery_app import celery


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, document_id: str) -> dict:
    """
    Full document pipeline: parse, chunk, embed, index.

    Steps are implemented incrementally in later milestones.
    """
    # TODO: parse -> chunk -> embed -> store in pgvector
    return {"document_id": document_id, "status": "pending"}
