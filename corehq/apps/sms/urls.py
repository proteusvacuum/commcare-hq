from django.conf.urls import patterns, url
from corehq import SMSAdminInterfaceDispatcher
from corehq.apps.sms.views import (
    DomainSmsGatewayListView,
    SubscribeSMSView,
    AddDomainGatewayView,
    EditDomainGatewayView,
    SMSSettingsView,
)

urlpatterns = patterns('corehq.apps.sms.views',
    url(r'^$', 'default', name='sms_default'),
    url(r'^post/?$', 'post', name='sms_post'),
    url(r'^send_to_recipients/$', 'send_to_recipients'),
    url(r'^compose/$', 'compose_message', name='sms_compose_message'),
    url(r'^message_test/(?P<phone_number>\d+)/$', 'message_test', name='message_test'),
    url(r'^api/send_sms/$', 'api_send_sms', name='api_send_sms'),
    url(r'^history/$', 'messaging', name='messaging'),
    url(r'^forwarding_rules/$', 'list_forwarding_rules', name='list_forwarding_rules'),
    url(r'^add_forwarding_rule/$', 'add_forwarding_rule', name='add_forwarding_rule'),
    url(r'^edit_forwarding_rule/(?P<forwarding_rule_id>[\w-]+)/$', 'add_forwarding_rule', name='edit_forwarding_rule'),
    url(r'^delete_forwarding_rule/(?P<forwarding_rule_id>[\w-]+)/$', 'delete_forwarding_rule', name='delete_forwarding_rule'),
    url(r'^add_gateway/(?P<backend_class_name>[\w-]+)/$',
        AddDomainGatewayView.as_view(), name=AddDomainGatewayView.urlname
    ),
    url(r'^edit_gateway/(?P<backend_class_name>[\w-]+)/(?P<backend_id>[\w-]+)/$',
        EditDomainGatewayView.as_view(), name=EditDomainGatewayView.urlname
    ),
    url(r'^gateways/$', DomainSmsGatewayListView.as_view(), name=DomainSmsGatewayListView.urlname),
    url(r'^chat_contacts/$', 'chat_contacts', name='chat_contacts'),
    url(r'^chat/(?P<contact_id>[\w-]+)/$', 'chat', name='sms_chat'),
    url(r'^api/history/$', 'api_history', name='api_history'),
    url(r'^api/last_read_message/$', 'api_last_read_message', name='api_last_read_message'),
    url(r'^settings_new/$', SMSSettingsView.as_view(), name='sms_settings_new'),
    url(r'^subscribe_sms/$', SubscribeSMSView.as_view(), name=SubscribeSMSView.urlname),
    url(r'^languages/$', 'sms_languages', name='sms_languages'),
    url(r'^languages/edit/$', 'edit_sms_languages', name='edit_sms_languages'),
    url(r'^translations/download/$', 'download_sms_translations', name='download_sms_translations'),
    url(r'^translations/upload/$', 'upload_sms_translations', name='upload_sms_translations'),
)

sms_admin_interface_urls = patterns('corehq.apps.sms.views',
    url(r'^$', 'default_sms_admin_interface', name="default_sms_admin_interface"),
    url(r'^backends/$', 'list_backends', name="list_backends"),
    url(r'^add_backend/(?P<backend_class_name>[\w-]+)/$', 'add_backend', name="add_backend"),
    url(r'^edit_backend/(?P<backend_class_name>[\w-]+)/(?P<backend_id>[\w-]+)/$', 'add_backend', name='edit_backend'),
    url(r'^delete_backend/(?P<backend_id>[\w-]+)/$', 'delete_backend', name='delete_backend'),
    url(r'^global_backend_map/$', 'global_backend_map', name='global_backend_map'),
    url(SMSAdminInterfaceDispatcher.pattern(), SMSAdminInterfaceDispatcher.as_view(),
        name=SMSAdminInterfaceDispatcher.name()),
)
