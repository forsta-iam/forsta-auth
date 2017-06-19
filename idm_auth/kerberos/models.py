from django.apps import apps
from django.contrib.auth.hashers import make_password, check_password, is_password_usable


class KerberosBackedUserMixin(object):
    def set_password(self, raw_password):
        if self.username:
            self.password = make_password(raw_password, salt=self.username, hasher='kerberos')
        else:
            if self.password and '$' in self.password:
                algorithm, _, principal, *_ = self.password.split('$')
                if algorithm == 'kerberos':
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
        preferred = 'kerberos' if self.username else 'default'
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
        return is_password_usable(self.password)

    def save(self, *args, **kwargs):
        if self.password and self.password.startswith('kerberos$'):
            algorithm, kvno, principal = self.password.split('$', 2)
            if algorithm == 'kerberos' and self.username and self.username != principal:
                kadmin = get_kadmin()
                kadmin.rename_principal(principal, self.username)
                self.password = '{}${}${}'.format(algorithm, kvno, self.username)
        return super().save(*args, **kwargs)
