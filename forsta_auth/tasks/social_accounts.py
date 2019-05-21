import logging
from urllib.parse import urljoin

from celery import shared_task
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from forsta_auth import settings

__all__ = ['sync_social_accounts']

logger = logging.getLogger(__name__)

provider_id_override = {
    'google-oauth2': 'google',
    'saml': None,
}

@shared_task
def sync_social_accounts(user_pk):
    from social_django.models import UserSocialAuth
    from forsta_auth.backend_meta import BackendMeta
    session = apps.get_app_config('forsta_auth').session

    user = get_user_model().objects.get(pk=user_pk)
    if not user.primary:
        return

    user_social_auths = UserSocialAuth.objects.filter(user=user)
    by_upstream_id = {str(usa.pk): usa
                      for usa in user_social_auths}
    online_account_url = urljoin(settings.IDM_CORE_API_URL, 'online-account/')

    results, url = [], online_account_url
    while url:
        response = session.get(url,
                               params={'identity': user.identity_id,
                                       'managed_by': settings.IDM_APPLICATION_ID})
        response.raise_for_status()
        response_data = response.json()
        results.extend(response_data['results'])
        url = response_data.get('next')

    for result in results:
        usa = by_upstream_id.get(result['upstream_id'])
        if usa:
            backend_meta = BackendMeta.wrap(usa)
            if backend_meta.username != result['screen_name']:
                session.patch(result['url'], json={'screen_name': backend_meta.username}).raise_for_status()
            del by_upstream_id[result['upstream_id']]
        else:
            session.delete(result['url']).raise_for_status()

    for upstream_id, usa in by_upstream_id.items():
        backend_meta = BackendMeta.wrap(usa)
        provider_id = provider_id_override.get(backend_meta.provider, backend_meta.provider)
        if provider_id is None:
            continue
        response = session.post(online_account_url, json={
            'identity': str(user.identity_id),
            'upstream_id': upstream_id,
            'provider_id': provider_id,
            'screen_name': backend_meta.username,
            'validated': True,
            'context': 'home',
            'managed': True,
            'manage_url': 'https://{}{}'.format(get_current_site(None).domain,
                                                reverse('social-logins'))
        })
        if not response.ok:
            logger.error("Couldn't create online-account:\n{}".format(response.content))
        response.raise_for_status()
