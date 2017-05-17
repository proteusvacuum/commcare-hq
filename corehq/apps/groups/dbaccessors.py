from django.conf import settings
from dimagi.utils.parsing import json_format_datetime

from corehq.apps.domain.dbaccessors import (
    get_docs_in_domain_by_class,
    get_doc_ids_in_domain_by_class,
)


def group_by_domain(domain):
    from corehq.apps.groups.models import Group
    return get_docs_in_domain_by_class(domain, Group)


def _group_by_name(domain, name, **kwargs):
    from corehq.apps.groups.models import Group
    return list(Group.view(
        'groups/by_name',
        key=[domain, name],
        **kwargs
    ))


def group_by_name(domain, name, include_docs=True):
    return _group_by_name(
        domain,
        name,
        include_docs=include_docs,
    )


def stale_group_by_name(domain, name, include_docs=True):
    return _group_by_name(
        domain,
        name,
        include_docs=include_docs,
        stale=settings.COUCH_STALE_QUERY,
    )


def refresh_group_views():
    from corehq.apps.groups.models import Group
    for view_name in [
        'groups/by_name',
    ]:
        Group.view(
            view_name,
            include_docs=False,
            limit=1,
        ).fetch()


def get_group_ids_by_domain(domain):
    from corehq.apps.groups.models import Group
    return get_doc_ids_in_domain_by_class(domain, Group)


def get_group_ids_by_last_modified(start_datetime, end_datetime):
    from corehq.apps.groups.models import Group

    return [result['id'] for result in Group.view(
        'group_last_modified/by_last_modified',
        startkey=json_format_datetime(start_datetime),
        endkey=json_format_datetime(end_datetime),
        include_docs=False,
        reduce=False,
    ).all()]
