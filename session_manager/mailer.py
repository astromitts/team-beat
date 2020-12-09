from django.conf import settings

from session_manager.models import EmailLog


def send_email(email_type, to_email, from_email, subject, body):
    if settings.LOG_EMAILS:
        email_log = EmailLog(
            email_type=email_type,
            to_email=to_email,
            from_email=from_email,
            subject=subject,
            body=body
        )
        email_log.save()
        return email_log
    return None
