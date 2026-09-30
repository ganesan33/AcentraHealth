from typing import Optional, List
from app.core.config import settings
from app.core.logging import logger


class AWSESIntegration:
    """Placeholder integration service for AWS Simple Email Service (SES)."""

    def __init__(
        self,
        sender_email: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        self.sender_email = sender_email or settings.AWS_SES_SENDER_EMAIL
        self.region_name = region_name or settings.AWS_REGION

    async def send_review_notification(
        self,
        recipient_emails: List[str],
        subject: str,
        body_text: str,
    ) -> bool:
        """
        Send a notification email via AWS SES.
        Placeholder implementation - boto3 send_email call to be implemented.
        """
        if not self.sender_email:
            logger.info(
                f"[AWS SES PLACEHOLDER] Send email to {recipient_emails} | Subject: '{subject}' "
                f"(Sender Email not configured)"
            )
            return True

        logger.info(
            f"[AWS SES PLACEHOLDER] Sending email from {self.sender_email} to {recipient_emails} | Subject: '{subject}'"
        )
        # Boto3 ses send_email implementation goes here
        return True


aws_ses_client = AWSESIntegration()
