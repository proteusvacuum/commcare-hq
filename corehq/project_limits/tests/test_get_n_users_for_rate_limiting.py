from django.test import TestCase

from corehq.apps.accounting.bootstrap.config.testing import BOOTSTRAP_CONFIG_TESTING
from corehq.apps.accounting.models import SoftwarePlanEdition, FeatureType, Subscription
from corehq.apps.accounting.tests.utils import DomainSubscriptionMixin
from corehq.apps.domain.shortcuts import create_domain
from corehq.apps.users.models import CommCareUser
from corehq.apps.users.util import format_username
from corehq.project_limits.rate_limiter import get_n_users_in_domain, get_n_users_in_subscription


class GetNUsersForRateLimitingTest(TestCase, DomainSubscriptionMixin):

    def test_no_subscription(self):
        domain = 'domain-no-subscription'
        domain_obj = create_domain(domain)
        self.addCleanup(domain_obj.delete)

        self._assert_domain_value_equals(domain, 0)

        self._set_n_users(domain, 1)

        self._assert_domain_value_equals(domain, 1)

    def test_with_subscription(self):

        domain_1 = 'domain-with-subscription'
        domain_2 = 'other-domain-in-same-customer-account'

        def _link_domains(domain, other_domain):
            plan_version = Subscription.get_active_subscription_by_domain(domain).plan_version
            plan = plan_version.plan
            plan.is_customer_software_plan = True
            plan.save()
            other_subscription = Subscription.get_active_subscription_by_domain(other_domain)
            other_subscription.plan_version = plan_version
            other_subscription.save()

        self._setup_domain(domain_1)

        # There are no users yet
        self._assert_domain_value_equals(domain_1, 0)

        # subscription value returns those included
        self._assert_subscription_value_equals(domain_1, 8)

        self._set_n_users(domain_1, 9)

        # With more users than included in subscription, it's the number of users
        self._assert_domain_value_equals(domain_1, 9)

        # subscription still returns only the billing amount
        self._assert_subscription_value_equals(domain_1, 8)

        self._setup_domain(domain_2)
        _link_domains(domain_1, domain_2)

        # No change on the original domain
        self._assert_domain_value_equals(domain_1, 9)

        # new domain has no users
        self._assert_domain_value_equals(domain_2, 0)

        # domain_2 still has full subscription allocation
        self._assert_subscription_value_equals(domain_2, 8)

    def test_no_user_limit(self):
        domain = 'enterprise-domain'
        self._setup_domain(domain, SoftwarePlanEdition.ENTERPRISE)
        self._assert_subscription_value_equals(domain, 1000)

    def _setup_domain(self, domain, software_plan=SoftwarePlanEdition.ADVANCED):
        domain_obj = create_domain(domain)
        self.setup_subscription(domain_obj.name, software_plan)
        self.addCleanup(lambda: self.teardown_subscription(domain))
        self.addCleanup(domain_obj.delete)
        assert CommCareUser.total_by_domain(domain, is_active=True) == 0

    def _assert_domain_value_equals(self, domain, value):
        get_n_users_in_domain.clear(domain)
        self.assertEqual(get_n_users_in_domain(domain), value)

    def _assert_subscription_value_equals(self, domain, value):
        get_n_users_in_subscription.clear(domain)
        self.assertEqual(get_n_users_in_subscription(domain), value)

    def _set_n_users(self, domain, n_users):
        start_n_users = CommCareUser.total_by_domain(domain, is_active=True)
        assert n_users >= start_n_users, 'this helper can only add users'

        for i in range(start_n_users, n_users):
            user = CommCareUser.create(domain, format_username('user{}'.format(i), domain),
                                       password='123', created_by=None, created_via=None)
            user.is_active = True
            user.save()
            self.addCleanup(user.delete, domain, deleted_by=None)
        assert CommCareUser.total_by_domain(domain, is_active=True) == n_users
