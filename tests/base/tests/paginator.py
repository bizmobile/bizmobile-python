from django.core.management import call_command
from django.core.paginator import Paginator
#from django.conf import settings; settings.DEBUG = True
from testcases import TestServerTestCase
#from .utils import id_generator

import bizmobile
from bizmobile.responsor import Responses


class PaginatorTestCase(TestServerTestCase):

    def setUp(self):
        super(PaginatorTestCase, self).setUp()
        self.start_test_server()
        call_command('loaddata', 'paginator_data.json')

    def tearDown(self):
        self.stop_test_server()

    def test_pagination1(self):

        api = bizmobile.connect.message(
            server="127.0.0.1:8001", api_name="base", secure=False)

        message = api._tester()
        p = Paginator(message, 100)
        self.assertTrue(p.count == 246)
        self.assertTrue(p.num_pages == 3)
        self.assertTrue(p.page_range == [1, 2, 3])

        page1 = p.page(1)
        self.assertTrue(isinstance(page1.object_list, Responses))
        self.assertTrue(page1.has_next() == True)
        self.assertTrue(page1.has_previous() == False)
        self.assertTrue(page1.has_other_pages() == True)
        self.assertTrue(page1.next_page_number() == 2)
        self.assertTrue(page1.previous_page_number() == 0)
        self.assertTrue(page1.start_index() == 1)
        self.assertTrue(page1.end_index() == 100)

        page2 = p.page(2)
        self.assertTrue(isinstance(page2.object_list, Responses))
        self.assertTrue(page2.has_next() == True)
        self.assertTrue(page2.has_previous() == True)
        self.assertTrue(page2.has_other_pages() == True)
        self.assertTrue(page2.next_page_number() == 3)
        self.assertTrue(page2.previous_page_number() == 1)
        self.assertTrue(page2.start_index() == 101)
        self.assertTrue(page2.end_index() == 200)

        page3 = p.page(3)
        self.assertTrue(isinstance(page3.object_list, Responses))
        self.assertTrue(page3.has_next() == False)
        self.assertTrue(page3.has_previous() == True)
        self.assertTrue(page3.has_other_pages() == True)
        self.assertTrue(page3.next_page_number() == 4)
        self.assertTrue(page3.previous_page_number() == 2)
        self.assertTrue(page3.start_index() == 201)
        self.assertTrue(page3.end_index() == 246)

        num = 0
        for num, i in enumerate(page1.object_list):
            print num, i
            pass
        self.assertTrue(num == 99)

        num = 0
        for num, i in enumerate(page2.object_list):
            print num, i
            pass
        self.assertTrue(num == 99)

        num = 0
        for num, i in enumerate(page3.object_list):
            print num, i
            pass
        self.assertTrue(num == 45)
