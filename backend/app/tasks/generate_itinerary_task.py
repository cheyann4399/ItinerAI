from celery import shared_task


@shared_task(name="app.tasks.generate_itinerary_task.generate_itinerary_task")
def generate_itinerary_task(payload: dict) -> dict:
  """
  Simple demo task for generating an itinerary-like structure.

  In later steps this can be replaced with real multi-agent orchestration.
  """
  title = payload.get("title", "未命名行程")
  days = int(payload.get("days", 1))

  summary = f"{title} - 共 {days} 天行程（示例任务）"

  return {
    "title": title,
    "days": days,
    "summary": summary,
  }

