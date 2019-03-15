import json
from collections import OrderedDict

from django.core import mail
from django.test import TestCase
from graphene.test import Client

from healthid.apps.authentication.models import User
from healthid.schema import schema

from .test_data import password_error_query, secondquery, userquery

class TestRegisterMutation(TestCase):

    def test_create_user_mutation(self):
        client = Client(schema)
        executed = client.execute(userquery)
        self.assertIn('success', executed['data']['createUser'])

    def test_register_mutation_user_error(self):
        client = Client(schema)
        executed = client.execute(secondquery)
        executed_second = client.execute(secondquery)
        self.assertIn('errors', executed_second['data']['createUser'])

    def test_create_wrong_password(self):
        client = Client(schema)
        executed = client.execute(password_error_query)
        self.assertIn('errors', executed)
 
    def test_mail_sent_successfully(self):
            """Tests whether the confirmation email was sent successfully"""
            client = Client(schema)
            executed = client.execute(userquery) 
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('success', executed['data']['createUser'])
