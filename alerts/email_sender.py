from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
from playsound import playsound

class EmailSender:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.recipient = os.getenv('EMAIL_RECIPIENT')
        self.sender = os.getenv('EMAIL_SENDER', self.smtp_user)

    def send_email(self, subject, body):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = self.recipient
        msg.set_content(body)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

        audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'audio/ringtone.mp3'))
        playsound(audio_path)
