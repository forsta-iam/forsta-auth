from django.apps import apps
from django.contrib.auth.hashers import make_password, check_password, is_password_usable, get_hasher, \
    get_hashers_by_algorithm
from django.utils.functional import cached_property

from forsta_auth.kerberos import KerberosAttribute
from forsta_auth.kerberos.apps import get_kadmin


class KerberosBackedUserMixin(object):
    @cached_property
    def kerberos_principal(self):
        if self.password.startswith('kerberos$'):
            return get_kadmin().get_principal(self.password.split('$', 3)[2])

    def set_password(self, raw_password):
        if self.username and 'kerberos' in get_hashers_by_algorithm():
            self.password = make_password(raw_password, salt=self.username, hasher='kerberos')
        else:
            if self.password and self.password.startswith('kerberos$'):
                algorithm, _, principal, *_ = self.password.split('$')
                kadmin = get_kadmin()
                if kadmin.principal_exists(principal):
                    kadmin.delete_principal(principal)
            self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        preferred = 'kerberos' if self.username and 'kerberos' in get_hashers_by_algorithm() else 'default'
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter, preferred=preferred)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        if self.kerberos_principal:
            return KerberosAttribute.DISALLOW_ALL_TIX.value not in self.kerberos_principal.attributes
        else:
            return is_password_usable(self.password)

    def save(self, *args, **kwargs):
        if self.password and self.password.startswith('kerberos$'):
            algorithm, kvno, principal = self.password.split('$', 2)
            if algorithm == 'kerberos' and self.username and self.username != principal:
                kadmin = get_kadmin()
                kadmin.rename_principal(principal, self.username)
                self.password = '{}${}${}'.format(algorithm, kvno, self.username)
        return super().save(*args, **kwargs)
