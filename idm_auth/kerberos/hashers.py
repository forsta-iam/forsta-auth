import kerberos
from collections import OrderedDict
from django.conf import settings

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.translation import ugettext_noop as _

from idm_auth.kerberos.apps import get_kadmin


class KerberosHasher(BasePasswordHasher):
    """
    A Django password hasher implementation backed by a Kerberos KDC

    Instead of hashing and storing the password on the user model, this hasher stores a reference to the password in the
    KDC and uses kerberos.checkPassword to validate it.

    For users without a username, it defaults to using the default password hasher, which we expect *will* store the
    password locally.

    We also store the kvno (incremented with every password change), so that when we change a password through the
    hasher Django knows to invalidate other sessions.
    """
    algorithm = 'kerberos'

    def encode(self, password, salt):
        kadmin = get_kadmin()
        if not kadmin.principal_exists(salt):
            kadmin.add_principal(salt)
        if password is None:
            kadmin.get_principal(salt).randomize_key()
        else:
            kadmin.change_password(salt, password)
        kvno = kadmin.get_principal(salt).kvno
        return 'kerberos${}${}'.format(kvno, salt)

    def salt(self):
        return super().salt()

    def must_update(self, encoded):
        return super().must_update(encoded)

    def verify(self, password, encoded):
        algorithm, kvno, principal = encoded.split('$', 2)
        try:
            return kerberos.checkPassword(principal, password,
                                          settings.CLIENT_PRINCIPAL_NAME,
                                          settings.DEFAULT_REALM)
        except kerberos.BasicAuthError:
            return False

    def safe_summary(self, encoded):
        algorithm, kvno, principal = encoded.split('$', 2)
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('principal'), principal),
            (_('kvno'), kvno),
        ])

    def harden_runtime(self, password, encoded):
        super().harden_runtime(password, encoded)

