from typing import Dict, Any
from app.workers.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(name="tasks.process_async_transaction_evaluation")
def process_async_transaction_evaluation(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to evaluate a transaction asynchronously in background.
    Placeholder task definition.
    """
    logger.info(f"Processing background transaction evaluation: {transaction_data.get('id')}")
    return {"status": "processed", "transaction_id": transaction_data.get("id")}


@celery_app.task(name="tasks.send_fraud_notification_task")
def send_fraud_notification_task(transaction_id: str, alert_details: Dict[str, Any]) -> bool:
    """
    Celery task to send fraud notifications via SNS/SES asynchronously.
    Placeholder task definition.
    """
    logger.info(f"Triggering asynchronous notification task for transaction: {transaction_id}")
    return True
