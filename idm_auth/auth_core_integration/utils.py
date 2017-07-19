from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings


def get_identity_url(identity_id):
    return '{}identity/{}/'.format(settings.IDM_CORE_API_URL, identity_id)


def get_identity_data(identity_id):
    session = apps.get_app_config('idm_auth').session
    response = session.get(get_identity_url(identity_id))
    response.raise_for_status()
    return response.json()['identity']


def update_user_from_identity(user, identity=None):
    from idm_auth.models import UserEmail

    if not identity:
        identity = get_identity_data(user.identity_id)

    user.state = identity['state']
    user.identity_type = identity['@type']

    if user.identity_type == 'Person':
        if identity.get('primary_name'):
            user.first_name = identity['primary_name']['first']
            user.last_name = identity['primary_name']['last']
        else:
            user.first_name = ''
            user.last_name = ''
    else:
        user.first_name = ''
        user.last_name = identity['label']

    if identity['state'] == 'established':
        for email in identity.get('emails', ()):
            if email['context'] == 'home':
                user.email = email['value']
                break
        else:
            user.email = ''
    else:
        validated_emails = [email['value']
                            for email in identity.get('emails', ())
                            if email['validated'] and user.primary]
        user.useremail_set.exclude(email__in=validated_emails).delete()
        UserEmail.objects.bulk_create([
            UserEmail(user=user, email=email)
            for email in validated_emails
            if email not in user.useremail_set.values_list('email', flat=True)
        ])


def activate_identity(user, identity_id):
    # Two things to do here:
    # 1. Tell idm-core that we've validated the user's email address
    # 2. Activate the identity record at idm-core

    session = apps.get_app_config('idm_auth').session

    # 1. Validate the email address, or create it if it wasn't already known about
    identity = get_identity_data(identity_id)
    for email in identity.get('emails', ()):
        if email['value'] == user.email:
            session.patch(email['url'], json={'validated': True})
            break
    else:
        response = session.post(urljoin(settings.IDM_CORE_API_URL, 'email/'), json={
            'identity': identity_id,
            'context': 'home',
            'value': user.email,
            'validated': True,
        })
        response.raise_for_status()

    # 2. Activate the identity
    response = session.post(get_identity_url(identity_id) + 'activate/')
    response.raise_for_status()
