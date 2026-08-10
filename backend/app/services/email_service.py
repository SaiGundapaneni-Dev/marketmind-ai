import smtplib
from email.message import EmailMessage
from html import escape
from app.core.config import settings

class EmailService:
    @staticmethod
    def send_password_reset(recipient: str, reset_url: str) -> bool:
        if not settings.email_configured:
            return False

        message = EmailMessage()
        message["Subject"] = "Reset your Vestora AI password"
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = recipient

        message.set_content(
            "You requested a password reset for Vestora AI.\n\n"
            f"Reset your password: {reset_url}\n\n"
            f"This link expires in {settings.password_reset_expire_minutes} minutes.\n\n"
            "If you did not request this, ignore this email."
        )

        safe_url = escape(reset_url, quote=True)
        message.add_alternative(
            f"""<html><body style="background:#020817;color:#e2e8f0;font-family:Arial;padding:32px">
            <div style="max-width:560px;margin:auto;background:#0f172a;border:1px solid #1e293b;border-radius:20px;padding:32px">
            <p style="color:#3b82f6;letter-spacing:2px;font-size:12px">VESTORA AI</p>
            <h1 style="color:white">Reset your password</h1>
            <p style="color:#94a3b8;line-height:1.7">Use the button below within {settings.password_reset_expire_minutes} minutes.</p>
            <p><a href="{safe_url}" style="display:inline-block;background:#3b82f6;color:white;text-decoration:none;padding:14px 20px;border-radius:12px;font-weight:bold">Reset password</a></p>
            <p style="color:#64748b;font-size:13px">If you did not request this, ignore this email.</p>
            </div></body></html>""",
            subtype="html",
        )

        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
            return True

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        return True
