from ..settings import *

BROKER_TRANSPORT = 'memory'

AUTHENTICATION_BACKENDS += ('idm_auth.tests.social_backend.DummyBackend',)