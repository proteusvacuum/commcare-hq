from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from corehq.apps.repeaters.models import CaseRepeater
from corehq.toggles import NIKSHAY_INTEGRATION
from casexml.apps.case.xml.parser import CaseUpdateAction
from casexml.apps.case.xform import get_case_updates


class NikshayRegisterPatientRepeater(CaseRepeater):
    class Meta(object):
        app_label = 'repeaters'

    include_app_id_param = False
    friendly_name = _("Forward eNikshay Patients to Nikshay")

    @classmethod
    def available_for_domain(cls, domain):
        return NIKSHAY_INTEGRATION.enabled(domain)

    @classmethod
    def get_custom_url(cls, domain):
        from custom.enikshay.integrations.nikshay.views import RegisterNikshayPatientRepeaterView
        return reverse(RegisterNikshayPatientRepeaterView.urlname, args=[domain])

    def allowed_to_forward(self, episode_case):
        # When case property episode.episode_pending_registration transitions from 'yes' to 'no',
        # and (episode.nikshay_registered != 'true'  or episode.nikshay_id != '')
        (not episode_case.nikshay_registered and
         not episode_case.nikshay_id and
         episode_pending_registration_changed(episode_case)
         )


def episode_pending_registration_changed(case):
    last_case_action = case.actions[-1]
    # previous_case_action = case.actions[-2]
    if last_case_action.is_case_create:
        return False

    last_update_actions = [update.get_update_action() for update in get_case_updates(last_case_action.form)]
    # add condition for if this is a create
    # previous_update_actions =
    # [update.get_update_action() for update in get_case_updates(previous_case_action.form)]
    value_changed = any(
        action for action in last_update_actions
        if isinstance(action, CaseUpdateAction)
        and 'episode_pending_registration' in action.dynamic_properties
        and action.dynamic_properties['episode_pending_registration'] == 'no'
    )
    return value_changed
