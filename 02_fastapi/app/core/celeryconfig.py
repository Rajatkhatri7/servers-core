from app.core.config import settings


broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_RESULT_BACKEND

task_serializer = 'json'
result_serializer='json'
accept_content=['json']
timezone="UTC"
enable_utc=True

task_routes = {
    'app.tasks.logging':{'queue':'default'}
}

