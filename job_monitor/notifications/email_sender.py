from __future__ import annotations

import smtplib
from email.message import EmailMessage


class EmailNotificationSender:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        email_from: str,
        email_to: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.email_from = email_from
        self.email_to = email_to

    def send(self, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.email_from
        message["To"] = self.email_to
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)

