from __future__ import absolute_import
from __future__ import unicode_literals

from django.db import transaction
from memoized import memoized

from dimagi.utils.logging import notify_exception
from corehq.util.test_utils import unit_testing_only


class IndicatorAdapter(object):
    def __init__(self, config):
        self.config = config

    @memoized
    def get_table(self):
        raise NotImplementedError

    def rebuild_table(self, initiated_by=None, source=None, skip_log=False):
        raise NotImplementedError

    def drop_table(self, initiated_by=None, source=None, skip_log=False):
        raise NotImplementedError

    @unit_testing_only
    def clear_table(self):
        raise NotImplementedError

    def get_query_object(self):
        raise NotImplementedError

    def best_effort_save(self, doc, eval_context=None):
        """
        Does a best-effort save of the document. Will fail silently if the save is not successful.

        For certain known, expected errors this will do no additional logging.
        For unexpected errors it will log them.
        """
        try:
            indicator_rows = self.get_all_values(doc, eval_context)
        except Exception as e:
            self.handle_exception(doc, e)
        else:
            self._best_effort_save_rows(indicator_rows, doc)

    def _best_effort_save_rows(self, rows, doc):
        """
        Like save rows, but should catch errors and log them
        """
        raise NotImplementedError

    def handle_exception(self, doc, exception):
        from corehq.util.cache_utils import is_rate_limited
        ex_clss = exception.__class__
        key = '{domain}.{table}.{ex_mod}.{ex_name}'.format(
            domain=self.config.domain,
            table=self.config.table_id,
            ex_mod=ex_clss.__module__,
            ex_name=ex_clss.__name__
        )
        if not is_rate_limited(key):
            notify_exception(
                None,
                'unexpected error saving UCR doc',
                details={
                    'domain': self.config.domain,
                    'doc_id': doc.get('_id', '<unknown>'),
                    'table': '{} ({})'.format(self.config.display_name, self.config._id)
                }
            )

    def save(self, doc, eval_context=None):
        """
        Saves the document. Should bubble up known errors.
        """
        indicator_rows = self.get_all_values(doc, eval_context)
        self.save_rows(indicator_rows)

    def save_rows(self, rows):
        raise NotImplementedError

    def bulk_save(self, docs):
        """
        Evalutes UCR rows for given docs and saves the result in bulk.
        """
        raise NotImplementedError

    def get_all_values(self, doc, eval_context=None):
        "Gets all the values from a document to save"
        return self.config.get_all_values(doc, eval_context)

    def bulk_delete(self, doc_ids):
        for _id in doc_ids:
            self.delete({'_id': _id})

    def delete(self, doc):
        raise NotImplementedError

    @property
    def run_asynchronous(self):
        return self.config.asynchronous

    def get_distinct_values(self, column, limit):
        raise NotImplementedError

    def log_table_build(self, initiated_by, source):
        from corehq.apps.userreports.models import DataSourceActionLog
        self._log_action(initiated_by, source, DataSourceActionLog.BUILD)

    def log_table_rebuild(self, initiated_by, source, skip=False):
        from corehq.apps.userreports.models import DataSourceActionLog
        self._log_action(initiated_by, source, DataSourceActionLog.REBUILD, skip=skip)

    def log_table_drop(self, initiated_by, source, skip=False):
        from corehq.apps.userreports.models import DataSourceActionLog
        self._log_action(initiated_by, source, DataSourceActionLog.DROP, skip=skip)

    def log_table_migrate(self, source, diffs):
        from corehq.apps.userreports.models import DataSourceActionLog
        self._log_action(None, source, DataSourceActionLog.MIGRATE, diffs=diffs)

    def _log_action(self, initiated_by, source, action, diffs=None, skip=False):
        from corehq.apps.userreports.models import DataSourceActionLog
        if skip or not self.config.data_source_id:
            return

        kwargs = {
            'domain': self.config.domain,
            'indicator_config_id': self.config.data_source_id,
            'action': action,
            'initiated_by': initiated_by,
            'action_source': source,
            'migration_diffs': diffs
        }

        try:
            # make this atomic so that errors don't affect outer transactions
            with transaction.atomic():
                DataSourceActionLog.objects.create(**kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # noqa
            # catchall to make sure errors here don't interfere with real workflows
            notify_exception(None, "Error saving UCR action log", details=kwargs)


class IndicatorAdapterLoadTracker(object):
    def __init__(self, adapter, track_load):
        self.adapter = adapter
        self._track_load = track_load

    def __getattr__(self, attr):
        return getattr(self.adapter, attr)

    def track_load(self, value=1):
        self._track_load(value)

    def save_rows(self, rows):
        self._track_load(len(rows))
        self.adapter.save_rows(rows)

    def delete(self, doc):
        self._track_load()
        self.adapter.delete(doc)

    def get_distinct_values(self, column, limit):
        distinct_values, too_many_values = self.adapter.get_distinct_values(column, limit)
        self._track_load(len(distinct_values))
        return distinct_values, too_many_values
