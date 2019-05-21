import logging

from django.apps import AppConfig
from django.conf import settings
import kadmin

logger = logging.getLogger(__name__)


class KerberosConfig(AppConfig):
    name = 'forsta_auth.kerberos'


def get_kadmin():
    try:
        return kadmin.init_with_keytab(settings.KADMIN_PRINCIPAL_NAME)
    except kadmin.CCNotFoundError:
        logger.exception("Couldn't get kadmin")
