from celery import Celery


celery_app = Celery(
    "app",
   
)
celery_app.config_from_object('app.core.celeryconfig')

celery_app.autodiscover_tasks(["app.tasks.logging",])