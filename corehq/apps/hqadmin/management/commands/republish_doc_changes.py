import itertools
from collections import namedtuple

from django.core.management import BaseCommand, CommandError

from corehq.apps.change_feed import data_sources, topics
from corehq.apps.change_feed.producer import producer
from corehq.apps.hqadmin.management.commands.stale_data_in_es import DataRow, HEADER_ROW
from corehq.form_processor.backends.sql.dbaccessors import ShardAccessor, doc_type_to_state
from corehq.form_processor.models import CommCareCaseSQL
from corehq.form_processor.utils import should_use_sql_backend
from dimagi.utils.chunked import chunked

from casexml.apps.case.models import CommCareCase
from corehq.util.couch import bulk_get_revs
from corehq.apps.hqcase.management.commands.backfill_couch_forms_and_cases import (
    publish_change, create_case_change_meta
)
from pillowtop.feed.interface import ChangeMeta


DocumentRecord = namedtuple('DocumentRecord', ['doc_id', 'doc_type', 'doc_subtype', 'domain'])


CASE_DOC_TYPES = {'CommCareCase'}
FORM_DOC_TYPES = set(doc_type_to_state.keys())


class Command(BaseCommand):
    """
    Republish doc changes. Meant to be used in conjunction with stale_data_in_es command

        $ ./manage.py republish_doc_changes changes.csv
    """

    def add_arguments(self, parser):
        parser.add_argument('stale_data_in_es_file')

    def handle(self, stale_data_in_es_file, *args, **options):
        data_rows = _get_data_rows(stale_data_in_es_file)
        document_records = _get_document_records(data_rows)
        form_records = []
        case_records = []
        for record in document_records:
            if record.doc_type in CASE_DOC_TYPES:
                case_records.append(record)
            elif record.doc_type in FORM_DOC_TYPES:
                form_records.append(record)
            else:
                assert False, f'Bad doc type {record.doc_type} should have been caught already below.'
        _publish_cases(case_records)
        _publish_forms(form_records)


def _get_data_rows(stale_data_in_es_file):
    with open(stale_data_in_es_file, 'r') as f:
        for line in f.readlines():
            data_row = DataRow(*line.rstrip('\n').split(','))
            # Skip the header row anywhere in the file.
            # The "anywhere in the file" part is useful
            # if you cat multiple stale_data_in_es_file files together.
            if data_row != HEADER_ROW:
                yield data_row


def _get_document_records(data_rows):
    for data_row in data_rows:
        doc_id, doc_type, doc_subtype, domain = \
            data_row.doc_id, data_row.doc_type, data_row.doc_subtype, data_row.domain
        if doc_type not in set.union(CASE_DOC_TYPES, FORM_DOC_TYPES):
            raise CommandError(f"Found bad doc type {doc_type}. "
                               "Did you use the right command to create the data?")
        yield DocumentRecord(doc_id, doc_type, doc_subtype, domain)


def _publish_cases(case_records):
    for domain, records in itertools.groupby(case_records, lambda r: r.domain):
        if should_use_sql_backend(domain):
            _publish_cases_for_sql(domain, records)
        else:
            _publish_cases_for_couch(domain, [c.doc_id for c in records])


def _publish_forms(form_records):
    for domain, records in itertools.groupby(form_records, lambda r: r.domain):
        if should_use_sql_backend(domain):
            _publish_forms_for_sql(domain, records)
        else:
            raise CommandError("Republishing forms for couch domains is not supported yet!")


def _publish_cases_for_couch(domain, case_ids):
    for ids in chunked(case_ids, 500):
        doc_id_rev_list = bulk_get_revs(CommCareCase.get_db(), ids)
        for doc_id, doc_rev in doc_id_rev_list:
            publish_change(
                create_case_change_meta(domain, doc_id, doc_rev)
            )


def _publish_cases_for_sql(domain, case_records):
    records_with_types = filter(lambda r: r.doc_subtype, case_records)
    records_with_no_types = filter(lambda r: not r.doc_subtype, case_records)
    # if we already had a type just publish as-is
    for record in records_with_types:
        producer.send_change(
            topics.CASE_SQL,
            _change_meta_for_sql_case(domain, record.doc_id, record.doc_subtype)
        )

    # else lookup the type from the database
    for record_chunk in chunked(records_with_no_types, 10000):
        # databases will contain a mapping of shard database ids to case_ids in that DB
        id_chunk = [r.doc_id for r in record_chunk]
        databases = ShardAccessor.get_docs_by_database(id_chunk)
        for db, doc_ids in databases.items():
            results = CommCareCaseSQL.objects.using(db).filter(
                case_id__in=doc_ids,
            ).values_list('case_id', 'type')
            # make sure we found the same number of IDs
            assert len(results) == len(doc_ids)
            for case_id, case_type in results:
                producer.send_change(
                    topics.CASE_SQL,
                    _change_meta_for_sql_case(domain, case_id, case_type)
                )


def _change_meta_for_sql_case(domain, case_id, case_type):
    doc_type, = CASE_DOC_TYPES
    return ChangeMeta(
        document_id=case_id,
        data_source_type=data_sources.SOURCE_SQL,
        data_source_name=data_sources.CASE_SQL,
        document_type=doc_type,
        document_subtype=case_type,
        domain=domain,
        is_deletion=False,
    )


def _publish_forms_for_sql(domain, form_records):
    for record in form_records:
        producer.send_change(
            topics.FORM_SQL,
            _change_meta_for_sql_form_record(domain, record)
        )


def _change_meta_for_sql_form_record(domain, form_record):
    return ChangeMeta(
        document_id=form_record.doc_id,
        data_source_type=data_sources.SOURCE_SQL,
        data_source_name=data_sources.FORM_SQL,
        document_type=form_record.doc_type,
        document_subtype=form_record.doc_subtype,
        domain=domain,
        is_deletion=False,
    )
