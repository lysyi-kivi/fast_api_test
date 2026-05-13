import time
from celery_app import celery_app

@celery_app.task
def send_welcome_email(email: str, username: str):
    # Имитация долгой задачи
    time.sleep(3)
    print(f"Письмо отправлено на {email} для {username}")
    return f"Email sent to {email}"

@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id: int):
    try:
        time.sleep(2)
        print(f"Заказ {order_id} обработан")
        return {"order_id": order_id, "status": "processed"}
    except Exception as exc:
        # Автоматический повтор через 5 секунд при ошибке
        raise self.retry(exc=exc, countdown=5)