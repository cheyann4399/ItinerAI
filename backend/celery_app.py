from celery import Celery

from app.core.celery_config import get_celery_settings


celery_settings = get_celery_settings()

celery_app = Celery(
  "itinerai",
  broker=celery_settings.celery_broker_url,
  backend=celery_settings.celery_result_backend,
)

celery_app.conf.update(
  task_default_queue=celery_settings.celery_task_default_queue,
  task_routes={
    "app.tasks.generate_itinerary_task.*": {"queue": "itinerary"},
  },
)

celery_app.autodiscover_tasks(
  packages=["app.tasks"],
)


