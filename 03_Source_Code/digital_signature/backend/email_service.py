import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> bool:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured. Cannot send OTP.")
            return False
            
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Kode OTP Login - IPB Lost & Found"
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email

        html = f"""
        <html>
          <body>
            <h2>IPB Lost & Found</h2>
            <p>Seseorang mencoba masuk ke akun Anda.</p>
            <p>Gunakan kode OTP berikut untuk melanjutkan proses login:</p>
            <h1 style="color: #4F46E5; letter-spacing: 5px;">{otp_code}</h1>
            <p>Kode ini hanya berlaku selama 5 menit.</p>
            <p>Jika ini bukan Anda, abaikan email ini dan pertimbangkan untuk mengubah password Anda.</p>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        msg.attach(part)

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
