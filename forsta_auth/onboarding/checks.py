import smtplib

from django.core import mail
from django.core.checks import Tags, Warning, register
from django.core.mail.backends.smtp import EmailBackend

W001 = Warning(
    "Unable to connect to an SMTP server. Ensure that the EMAIL_* settings are correctly configured.",
    id='onboarding.W001',
)


@register('integration', deploy=True)
def check_email_config(app_configs, **kwargs):
    """Ensures we can connect to an email server

    Doesn't check whether authentication would be required if none is configured, but will check credentials if they
    are provided. This will therefore catch expired or no-longer-valid credentials."""
    connection = mail.get_connection()
    if isinstance(connection, EmailBackend):
        try:
            connection.open()
        except smtplib.SMTPAuthenticationError:
            return [W001]
    return []
