#from django.conf import settings; settings.DEBUG = True
from django.core.management import call_command
from django.db.models.query import (
    QuerySet,
    ValuesListQuerySet
)
from testcases import TestServerTestCase
import bizmobile


class ToValuesTestCase(TestServerTestCase):

    def setUp(self):
        super(ToValuesTestCase, self).setUp()
        self.start_test_server()
        self.api = bizmobile.connect.message(
            server="127.0.0.1:8001", api_name="base", secure=False, auth=False)
        call_command('loaddata', 'base_data.json')

    def tearDown(self):
        self.stop_test_server()

    def test_to_values1(self):
        from base.models import Message

        vqs = Message.objects.extra(
            select={'mailto': 'id'}).values("subject", "body", "mailfrom", "mailto")

        self._ok(vqs)
        self._ok(vqs._clone(klass=QuerySet))
        self._ok(vqs._clone(klass=ValuesListQuerySet))
        self._ok(list(vqs))
        # self._ok(vqs[0])
        print vqs

    def _ok(self, queryset):
        self.assertTrue(isinstance(self.api._to_values(queryset), (list, set)))
