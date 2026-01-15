import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

class Mailer:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def send_email(self, to_email, subject, html_body, text_body=None):
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not present. Skipping email send (dry run mode).")
            logger.info(f"Would have sent email to {to_email} with subject: {subject}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"TirwinPulse <{self.smtp_user}>"
            msg["To"] = to_email

            if text_body:
                part1 = MIMEText(text_body, "plain")
                msg.attach(part1)
            
            part2 = MIMEText(html_body, "html")
            msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
