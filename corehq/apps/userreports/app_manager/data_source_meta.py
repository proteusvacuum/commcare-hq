

DATA_SOURCE_TYPE_CASE = 'case'
DATA_SOURCE_TYPE_FORM = 'form'
DATA_SOURCE_TYPE_VALUES = (DATA_SOURCE_TYPE_CASE, DATA_SOURCE_TYPE_FORM)
DATA_SOURCE_TYPE_CHOICES = (
    (DATA_SOURCE_TYPE_CASE, _("Cases")),
    (DATA_SOURCE_TYPE_FORM, _("Forms")),
)
DATA_SOURCE_DOC_TYPE_MAPPING = {
    DATA_SOURCE_TYPE_CASE: 'CommCareCase',
    DATA_SOURCE_TYPE_FORM: 'XFormInstance',
}


def get_data_source_doc_type(data_source_type):
    return DATA_SOURCE_DOC_TYPE_MAPPING[data_source_type]
