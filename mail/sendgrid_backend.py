import os
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sg = SendGridAPIClient(os.environ.get("EMAIL_HOST_PASSWORD"))
        for message in email_messages:
            mail = Mail(
                from_email=message.from_email,
                to_emails=message.to,
                subject=message.subject,
                plain_text_content=message.body,
                html_content=message.alternatives[0][0] if message.alternatives else None,
            )
            try:
                sg.send(mail)
            except Exception as e:
                if not self.fail_silently:
                    raise
        return len(email_messages)
