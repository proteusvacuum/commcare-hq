import json

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from unittest import mock

from corehq.apps.domain.shortcuts import create_domain
from corehq.apps.es.tests.utils import es_test
from corehq.apps.es.users import user_adapter
from corehq.apps.locations.exceptions import LocationConsistencyError
from corehq.apps.locations.models import LocationType
from corehq.apps.locations.tests.util import make_loc
from corehq.apps.locations.views import LocationTypesView
from corehq.util.test_utils import flag_enabled
from corehq.apps.users.dbaccessors import delete_all_users
from corehq.apps.users.models import WebUser


OTHER_DETAILS = {
    'expand_from': None,
    'expand_to': None,
    'expand_from_root': False,
    'include_without_expanding': None,
    'include_only': [],
    'parent_type': '',
    'administrative': '',
    'shares_cases': False,
    'view_descendants': False,
    'expand_view_child_data_to': None,
    'has_users': True,
}


@es_test(requires=[user_adapter])
class LocationTypesViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(LocationTypesViewTest, cls).setUpClass()
        cls.domain = "test-domain"
        cls.project = create_domain(cls.domain)
        cls.couch_user = WebUser.create(cls.domain, "test", "foobar", None, None)
        cls.couch_user.add_domain_membership(cls.domain, is_admin=True)
        cls.couch_user.set_role(cls.domain, "admin")
        cls.couch_user.save()
        cls.loc_type1 = LocationType(domain=cls.domain, name='type1', code='code1')
        cls.loc_type1.save()
        cls.loc_type2 = LocationType(domain=cls.domain, name='type2', code='code2')
        cls.loc_type2.save()

    def setUp(self):
        self.url = reverse(LocationTypesView.urlname, args=[self.domain])
        self.client = Client()
        self.client.login(username='test', password='foobar')

    @classmethod
    def tearDownClass(cls):
        cls.couch_user.delete(cls.domain, deleted_by=None)
        cls.project.delete()
        super(LocationTypesViewTest, cls).tearDownClass()

    @mock.patch('django_prbac.decorators.has_privilege', return_value=True)
    def send_request(self, data, _):
        return self.client.post(self.url, {'json': json.dumps(data)})

    def test_missing_property(self):
        with self.assertRaises(LocationConsistencyError):
            self.send_request({'loc_types': [{}]})

    def test_swap_name(self):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': self.loc_type2.name, 'pk': self.loc_type1.pk})
        loc_type2.update({'name': self.loc_type1.name, 'pk': self.loc_type2.pk})
        data = {'loc_types': [loc_type1, loc_type2]}
        response = self.send_request(data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0].message),
            'Looks like you are assigning a location name/code to a different location in the same request. '
            'Please do this in two separate updates by using a temporary name to free up the name/code to be '
            're-assigned.'
        )

    def test_swap_code(self):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': self.loc_type1.name, 'pk': self.loc_type1.pk, 'code': self.loc_type2.code})
        loc_type2.update({'name': self.loc_type2.name, 'pk': self.loc_type2.pk, 'code': self.loc_type1.code})
        data = {'loc_types': [loc_type1, loc_type2]}
        response = self.send_request(data)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0].message),
            'Looks like you are assigning a location name/code to a different location in the same request. '
            'Please do this in two separate updates by using a temporary name to free up the name/code to be '
            're-assigned.'
        )

    def test_valid_update(self):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': "new name", 'pk': self.loc_type1.pk, 'code': self.loc_type1.code})
        loc_type2.update({'name': "new name 2", 'pk': self.loc_type2.pk, 'code': self.loc_type2.code})
        data = {'loc_types': [loc_type1, loc_type2]}
        response = self.send_request(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_hierarchy(self):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': "new name", 'pk': self.loc_type1.pk, 'code': self.loc_type1.code})
        loc_type2.update({'name': "new name 2", 'pk': self.loc_type2.pk, 'parent_type': self.loc_type1.pk,
                          'code': self.loc_type2.code})
        data = {'loc_types': [loc_type1, loc_type2]}
        response = self.send_request(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_child_data(self):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': "new name", 'pk': self.loc_type1.pk,
                          'view_descendants': True, 'expand_view_child_data_to': self.loc_type2.pk,
                          'code': self.loc_type1.code, 'shares_cases': True, 'has_users': True})
        loc_type2.update({'name': "new name 2", 'pk': self.loc_type2.pk, 'parent_type': self.loc_type1.pk,
                          'code': self.loc_type2.code})
        data = {'loc_types': [loc_type1, loc_type2]}
        response = self.send_request(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_invalid_child_data(self):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': "new name", 'pk': self.loc_type1.pk, 'code': self.loc_type1.code})
        loc_type2.update({'name': "new name 2", 'pk': self.loc_type2.pk, 'parent_type': self.loc_type1.pk,
                          'view_descendants': True, 'expand_view_child_data_to': self.loc_type1.pk,
                          'code': self.loc_type2.code})
        data = {'loc_types': [loc_type1, loc_type2]}
        with self.assertRaises(LocationConsistencyError):
            self.send_request(data)

    @flag_enabled('LOCATION_HAS_USERS')
    @mock.patch('corehq.apps.locations.views.does_location_type_have_users', return_value=True)
    def test_invalid_remove_has_users(self, _):
        loc_type1 = OTHER_DETAILS.copy()
        loc_type2 = OTHER_DETAILS.copy()
        loc_type1.update({'name': "new name", 'pk': self.loc_type1.pk, 'code': self.loc_type1.code,
                          'has_users': False})
        loc_type2.update({'name': "new name 2", 'pk': self.loc_type2.pk, 'parent_type': self.loc_type1.pk,
                          'code': self.loc_type2.code})
        data = {'loc_types': [loc_type1, loc_type2]}
        with self.assertRaises(LocationConsistencyError):
            self.send_request(data)


class LocationsSearchViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(LocationsSearchViewTest, cls).setUpClass()
        delete_all_users()
        cls.domain = "test-domain"
        cls.project = create_domain(cls.domain)
        cls.username = "request-er"
        cls.password = "foobar"
        cls.web_user = WebUser.create(cls.domain, cls.username, cls.password, None, None)
        cls.web_user.add_domain_membership(cls.domain, is_admin=True)
        cls.web_user.set_role(cls.domain, "admin")
        cls.web_user.save()
        cls.loc_type1 = LocationType(domain=cls.domain, name='type1', code='code1')
        cls.loc_type1.save()
        cls.loc1 = make_loc(
            'loc_1', type=cls.loc_type1, domain=cls.domain
        )
        cls.loc2 = make_loc(
            'loc_2', type=cls.loc_type1, domain=cls.domain
        )

    def setUp(self):
        self.client.login(username=self.username, password=self.password)

    @classmethod
    def tearDownClass(cls):
        cls.project.delete()
        delete_all_users()
        return super().tearDownClass()

    @mock.patch('django_prbac.decorators.has_privilege', return_value=True)
    def send_request(self, url, data, _):
        return self.client.get(url, {'json': json.dumps(data)})

    def test_search_view_basic(self):
        url = reverse('location_search', args=[self.domain])
        data = {'q': 'loc'}
        response = self.send_request(url, data)
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content)['results']
        self.assertEqual(results[0]['id'], self.loc1.location_id)
        self.assertEqual(results[1]['id'], self.loc2.location_id)

    @flag_enabled('LOCATION_HAS_USERS')
    def test_search_view_has_users_only(self):
        loc_type2 = LocationType(domain=self.domain, name='type2', code='code2')
        loc_type2.has_users = False
        loc_type2.save()
        self.loc3 = make_loc(
            'loc_3', type=loc_type2, domain=self.domain
        )
        self.loc3 = make_loc(
            'loc_4', type=loc_type2, domain=self.domain
        )
        url = reverse('location_search_has_users_only', args=[self.domain])
        data = {'q': 'loc'}
        response = self.send_request(url, data)
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.content)['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], self.loc1.location_id)
        self.assertEqual(results[1]['id'], self.loc2.location_id)
