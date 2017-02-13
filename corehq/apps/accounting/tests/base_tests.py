from __future__ import absolute_import
from django.test import TestCase
from django_prbac.models import Role

from corehq.apps.accounting.tests import generator
from corehq.apps.domain.models import Domain


class BaseAccountingTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseAccountingTest, cls).setUpClass()
        Role.get_cache().clear()
        generator.instantiate_accounting()

    @classmethod
    def tearDownClass(cls):
        for domain in Domain.get_all():
            domain.delete()
        super(BaseAccountingTest, cls).tearDownClass()
