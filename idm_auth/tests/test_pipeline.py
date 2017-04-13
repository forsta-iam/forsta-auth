import threading
import time
import uuid
from unittest import mock
from unittest.mock import Mock

import kombu
from django.apps import apps
from django.test import TestCase
from kombu.message import Message

from idm_auth.pipeline.creation import create_user
from idm_auth.tests.utils import IDMAuthDaemonTestCaseMixin, creates_idm_core_user, GeneratesMessage


class CreateUserTestCase(IDMAuthDaemonTestCaseMixin, TestCase):
    """Tests our use of our create_user pipeline element in python-social-auth'"""

    def testDoesNothingIfUserFound(self):
        kwargs = {'user': Mock()}
        result = create_user(**kwargs)
        self.assertFalse(result)

    @creates_idm_core_user
    def testCreation(self, identity_id):
        kwargs = {'details': {'first_name': 'Lewis', 'last_name': 'Carroll',
                              'email': 'lewiscarroll@example.org', 'date_of_birth': '1832-01-27'}}
        with GeneratesMessage('idm.auth.user') as gm:
            result = create_user(**kwargs)
        self.assertIsInstance(gm.message, Message)