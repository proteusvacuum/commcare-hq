from django.utils.translation import ugettext as _

from corehq.apps.locations.models import Location
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumn, NumericColumn
from corehq.apps.reports.fields import AsyncLocationField
from corehq.apps.reports.filters.select import MonthFilter, YearFilter
from corehq.apps.reports.standard import CustomProjectReport, MonthYearMixin
from corehq.apps.reports.standard.cases.basic import CaseListReport
from custom.m4change.reports.reports import M4ChangeReport
from custom.m4change.reports.sql_data import AncHmisCaseSqlData, LdHmisCaseSqlData


def _get_row(row_data, form_data, key):
    data = form_data.get(key)
    rows = dict([(row_key, data.get(row_key, 0)) for row_key in row_data])
    for key in rows:
        if rows.get(key) == None:
            rows[key] = 0
    return rows


class LdHmisReport(MonthYearMixin, CustomProjectReport, CaseListReport, M4ChangeReport):
    ajax_pagination = False
    asynchronous = True
    exportable = True
    emailable = False
    name = "Facility L&D HMIS Report"
    slug = "facility_ld_hmis_report"
    default_rows = 25

    fields = [
        AsyncLocationField,
        MonthFilter,
        YearFilter
    ]

    @classmethod
    def get_report_data(cls, config):
        if "location_id" not in config:
            raise KeyError(_("Parameter 'location_id' is missing"))
        if "datespan" not in config:
            raise KeyError(_("Parameter 'datespan' is missing"))
        if 'domain' not in config:
            raise KeyError(_("Parameter 'domain' is missing"))

        domain = config.get('domain', None)
        location_id = config.get("location_id", None)
        sql_data = LdHmisCaseSqlData(domain=domain, datespan=config.get("datespan", None)).data
        top_location = Location.get(location_id)
        locations = [location_id] + [descendant.get_id for descendant in top_location.descendants]
        row_data = LdHmisReport.get_initial_row_data()

        for location_id in locations:
            key = (domain, location_id)
            if key in sql_data:
                report_rows = _get_row(row_data, sql_data, key)
                for key in report_rows:
                    row_data.get(key)["value"] += report_rows.get(key)
        return row_data


    @classmethod
    def get_initial_row_data(cls):
        return {
            "deliveries_total": {
                "hmis_code": 19, "label": _("Deliveries - Total"), "value": 0
            },
            "deliveries_svd_total": {
                "hmis_code": 20, "label": _("Deliveries - SVD"), "value": 0
            },
            "deliveries_assisted_total": {
                "hmis_code": 21, "label": _("Deliveries - Assisted"), "value": 0
            },
            "deliveries_caesarean_section_total": {
                "hmis_code": 22, "label": _("Deliveries caesarean section"), "value": 0
            },
            "deliveries_complications_total": {
                "hmis_code": 23, "label": _("Deliveries - Complications"), "value": 0
            },
            'deliveries_preterm_total': {
                "hmis_code": 24, "label": _("Deliveries - Preterm"), "value": 0
            },
            'deliveries_hiv_positive_women_total': {
                "hmis_code": 25, "label": _("Deliveries - HIV positive women"), "value": 0
            },
            'live_birth_hiv_positive_women_total': {
                "hmis_code": 26, "label": _("LiveBirth - HIV positive women"), "value": 0
            },
            'deliveries_hiv_positive_booked_women_total': {
                "hmis_code": 27, "label": _("Deliveries - HIV positive booked women"), "value": 0
            },
            'deliveries_hiv_positive_unbooked_women_total': {
                "hmis_code": 28, "label": _("Deliveries - HIV positive unbooked women"), "value": 0
            },
            'deliveries_monitored_using_partograph_total': {
                "hmis_code": 29, "label": _("Deliveries - Monitored using Partograph"), "value": 0
            },
            'deliveries_skilled_birth_attendant_total': {
                "hmis_code": 30, "label": _("Deliveries taken by skilled birth attendant"), "value": 0
            },
            'tt1_total': {
                "hmis_code": 31, "label": _("TT1"), "value": 0
            },
            'tt2_total': {
                "hmis_code": 32, "label": _("TT2"), "value": 0
            },
            'live_births_male_female_total': {
                "hmis_code": 36, "label": _("Live Births(Male, Female, < 2.5kg, >= 2.5k g)"), "value": 0
            },
            'male_lt_2_5kg_total': {
                "hmis_code": 36.1, "label": _("Male, < 2.5kg"), "value": 0
            },
            'male_gte_2_5kg_total': {
                "hmis_code": 36.2, "label": _("Male, >= 2.5kg"), "value": 0
            },
            'female_lt_2_5kg_total': {
                "hmis_code": 36.3, "label": _("Female, < 2.5kg"), "value": 0
            },
            'female_gte_2_5kg_total': {
                "hmis_code": 36.4, "label": _("Female, >= 2.5kg"), "value": 0
            },
            'still_births_total': {
                "hmis_code": 37, "label": _("Still Births total"), "value": 0
            },
            'fresh_still_births_total': {
                "hmis_code": 38.1, "label": _("Fresh Still Births"), "value": 0
            },
            'other_still_births_total': {
                "hmis_code": 38.2, "label": _("Other still Births"), "value": 0
            },
            'abortion_induced_total': {
                "hmis_code": 39.1, "label": _("Abortion Induced"), "value": 0
            },
            'other_abortions_total': {
                "hmis_code": 39.2, "label": _("Other Abortions"), "value": 0
            },
            'total_abortions_total': {
                "hmis_code": 40, "label": _("Total Abortions"), "value": 0
            },
            'birth_asphyxia_total': {
                "hmis_code": 41, "label": _("Birth Asphyxia - Total"), "value": 0
            },
            'birth_asphyxia_male_total': {
                "hmis_code": 41.1, "label": _("Birth Asphyxia - Male"), "value": 0
            },
            'birth_asphyxia_female_total': {
                "hmis_code": 41.2, "label": _("Birth Asphyxia - Female"), "value": 0
            },
            'neonatal_sepsis_total': {
                "hmis_code": 42, "label": _("Neonatal Sepsis - Total"), "value": 0
            },
            'neonatal_sepsis_male_total': {
                "hmis_code": 42.1, "label": _("Neonatal Sepsis - Male"), "value": 0
            },
            'neonatal_sepsis_female_total': {
                "hmis_code": 42.2, "label": _("Neonatal Sepsis - Female"), "value": 0
            },
            'neonatal_tetanus_total': {
                "hmis_code": 43, "label": _("Neonatal Tetanus - Total"), "value": 0
            },
            'neonatal_tetanus_male_total': {
                "hmis_code": 43.1, "label": _("Neonatal Tetanus - Male"), "value": 0
            },
            'neonatal_tetanus_female_total': {
                "hmis_code": 43.2, "label": _("Neonatal Tetanus - Female"), "value": 0
            },
            'neonatal_jaundice_total': {
                "hmis_code": 44, "label": _("Neonatal Jaundice - Total"), "value": 0
            },
            'neonatal_jaundice_male_total': {
                "hmis_code": 44.1, "label": _("Neonatal Jaundice - Male"), "value": 0
            },
            'neonatal_jaundice_female_total': {
                "hmis_code": 44.2, "label": _("Neonatal Jaundice - Female"), "value": 0
            },
            'low_birth_weight_babies_in_kmc_total': {
                "hmis_code": 45, "label": _("Low birth weight babies placed in KMC - Total"), "value": 0
            },
            'low_birth_weight_babies_in_kmc_male_total': {
                "hmis_code": 45.1, "label": _("Low birth weight babies placed in KMC - Male"), "value": 0
            },
            'low_birth_weight_babies_in_kmc_female_total': {
                "hmis_code": 45.2, "label": _("Low birth weight babies placed in KMC - Female"), "value": 0
            },
            'newborns_low_birth_weight_discharged_total': {
                "hmis_code": 46, "label": _("Newborns with low birth weight discharged - Total"), "value": 0
            },
            'newborns_low_birth_weight_discharged_male_total': {
                "hmis_code": 46.1, "label": _("Newborns with low birth weight discharged - Male"), "value": 0
            },
            'newborns_low_birth_weight_discharged_female_total': {
                "hmis_code": 46.2, "label": _("Newborns with low birth weight discharged - Female"), "value": 0
            }
        }

    @property
    def headers(self):
        headers = DataTablesHeader(NumericColumn(_("HMIS code")),
                                   DataTablesColumn(_("Data Point")),
                                   NumericColumn(_("Total")))
        return headers

    @property
    def rows(self):
        row_data = LdHmisReport.get_report_data({
            "location_id": self.request.GET.get("location_id", None),
            "datespan": self.datespan,
            "domain": str(self.domain)
        })

        for key in row_data:
            yield [
                self.table_cell(row_data.get(key).get("hmis_code")),
                self.table_cell(row_data.get(key).get("label")),
                self.table_cell(row_data.get(key).get("value"))
            ]

    @property
    def rendered_report_title(self):
        return self.name
