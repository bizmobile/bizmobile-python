#from django.conf import settings; settings.DEBUG = True
from django.core.management import call_command
from django.db.models.query import (
    QuerySet,
    ValuesListQuerySet
)
from testcases import TestServerTestCase
import bizmobile


class PaginatorTestCase(TestServerTestCase):

    def setUp(self):
        super(PaginatorTestCase, self).setUp()
        self.start_test_server()
        call_command('loaddata', 'base_data.json')

    def tearDown(self):
        self.stop_test_server()

    def test_to_values1(self):
        from base.models import Message

        api = bizmobile.connect.message(
            server="127.0.0.1:8001", api_name="base", secure=False)

        vqs = Message.objects.extra(
            select={'mailto': 'id'}).values("subject", "body", "mailfrom", "mailto")

        self.assrtTrue(isinstance(api._to_values(vqs), (list, set)))
        self.assrtTrue(isinstance(api._to_values(vqs._clone(klass=QuerySet)), (list, set)))
        self.assrtTrue(isinstance(api._to_values(vqs._clone(klass=ValuesListQuerySet)), (list, set)))
        self.assrtTrue(isinstance(api._to_values(list(vqs)), (list, set)))
        self.assrtTrue(isinstance(api._to_values(vqs[0]), (list, set)))
