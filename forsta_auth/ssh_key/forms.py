import sshpubkeys
from django import forms
from django.core.exceptions import ValidationError

from . import models


class SSHKeyForm(forms.ModelForm):
    label = forms.CharField(required=False)

    def clean_key(self):
        key = sshpubkeys.SSHKey(self.cleaned_data['key'], strict_mode=True)
        try:
            key.parse()
        except NotImplementedError:
            raise ValidationError("There was an error parsing the given key") from e
        except sshpubkeys.TooShortKeyException as e:
            raise ValidationError(
                'Key is too short (should be at least 768 bits for RSA, 1024 for DSA, or 256 for ED25519') from e
        except sshpubkeys.TooLongKeyException as e:
            raise ValidationError(
                'Key is too long (should be at most 16384 bits for RSA, 1024 for DSA, or 256 for ED25519') from e
        except sshpubkeys.InvalidKeyException as e:
            raise ValidationError("There was an error parsing the given key") from e
        if not self.cleaned_data.get('label'):
            self.cleaned_data['label'] = key.comment

        return key.keydata

    class Meta:
        model = models.SSHKey
        fields = ('label', 'key')
