from typing import Dict, Any, Optional
from app.core.logging import logger
from app.integrations.aws_sns import AWSNSIntegration, aws_sns_client
from app.integrations.aws_ses import AWSESIntegration, aws_ses_client


class NotificationService:
    """Service handling multi-channel alert dispatch (SNS, SES, logs) for fraud events."""

    def __init__(
        self,
        sns_client: Optional[AWSNSIntegration] = None,
        ses_client: Optional[AWSESIntegration] = None,
    ) -> None:
        self.sns_client = sns_client or aws_sns_client
        self.ses_client = ses_client or aws_ses_client

    async def send_fraud_alert(
        self,
        transaction_id: str,
        risk_score: float,
        decision: str,
        details: Dict[str, Any],
    ) -> None:
        """Dispatch high-risk transaction alerts to operations channels."""
        message = (
            f"[FRAUD ALERT] Transaction {transaction_id} flagged with decision '{decision}' "
            f"(Risk Score: {risk_score:.1f}/100).\nDetails: {details}"
        )
        logger.warning(message)

        # Dispatch SNS alert
        try:
            await self.sns_client.publish_fraud_alert(
                transaction_id=transaction_id,
                alert_data={"risk_score": risk_score, "decision": decision, "details": details},
            )
        except Exception as e:
            logger.error(f"Failed to publish SNS alert: {e}")

        # Dispatch SES Email if critical threshold met
        if risk_score >= 80.0:
            try:
                await self.ses_client.send_review_notification(
                    recipient_emails=["fraud-alerts@company.internal"],
                    subject=f"Critical Fraud Alert: Transaction {transaction_id}",
                    body_text=message,
                )
            except Exception as e:
                logger.error(f"Failed to send SES alert email: {e}")
