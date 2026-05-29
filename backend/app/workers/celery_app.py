from celery import Celery, Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(
        app.name,
        task_cls=FlaskTask,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
        include=["app.workers.document_tasks"],
        broker_connection_retry_on_startup=True,
    )
    celery.conf.beat_schedule = {
        "retry-stuck-documents": {
            "task": "app.workers.document_tasks.retry_stuck_documents",
            "schedule": 300.0,  # every 5 minutes
        },
    }
    celery.set_default()
    app.extensions["celery"] = celery
    return celery
