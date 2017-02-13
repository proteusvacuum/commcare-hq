# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion

import jsonfield.fields

from corehq.apps.accounting.bootstrap.config.report_builder_v0 import BOOTSTRAP_CONFIG as report_builder_config
from corehq.apps.accounting.bootstrap.config.resellers_and_managed_hosting import BOOTSTRAP_CONFIG as resellers_config
from corehq.apps.accounting.bootstrap.config.user_buckets_jan_2017 import BOOTSTRAP_CONFIG as self_service_config
from corehq.apps.accounting.bootstrap.utils import ensure_plans
from corehq.apps.hqadmin.management.commands.cchq_prbac_bootstrap import cchq_prbac_bootstrap
from corehq.sql_db.operations import HqRunPython
import corehq.util.mixin


def _cchq_software_plan_bootstrap(apps, schema_editor):
    pricing_config = self_service_config
    pricing_config.update(report_builder_config)
    pricing_config.update(resellers_config)
    ensure_plans(pricing_config, dry_run=False, verbose=True, apps=apps)


class Migration(migrations.Migration):

    replaces = [(b'accounting', '0001_initial'), (b'accounting', '0002_update_pricing_table'), (b'accounting', '0003_bootstrap'), (b'accounting', '0004_subscription_no_invoice_reason'), (b'accounting', '0003_auto_20150903_1855'), (b'accounting', '0004_merge'), (b'accounting', '0005_merge'), (b'accounting', '0006_remove_organization_field'), (b'accounting', '0007_make_subscriber_domain_required'), (b'accounting', '0008_auto_20151120_1652'), (b'accounting', '0009_add_extended_trial_subscription_type'), (b'accounting', '0010_add_do_not_email'), (b'accounting', '0011_subscription_is_hidden_to_ops'), (b'accounting', '0012_billing_metadata_data_migration'), (b'accounting', '0013_forbid_feature_type_any'), (b'accounting', '0014_billingcontactinfo_email_list'), (b'accounting', '0015_datamigration_email_list'), (b'accounting', '0016_remove_billingcontactinfo_emails'), (b'accounting', '0017_add_product_rate'), (b'accounting', '0018_datamigration_product_rates_to_product_rate'), (b'accounting', '0019_remove_softwareplanversion_product_rates'), (b'accounting', '0020_nonnullable_product_rate'), (b'accounting', '0021_remove_old_roles'), (b'accounting', '0022_bootstrap_prbac_roles'), (b'accounting', '0023__simplify__credit_line__product_type'), (b'accounting', '0024_date_created_to_datetime'), (b'accounting', '0025_creditadjustment_permit_blank_fields'), (b'accounting', '0026_subscriber_domain_unique'), (b'accounting', '0027_auto_20160422_1744'), (b'accounting', '0028_bootstrap_new_editions'), (b'accounting', '0027_remove_subscriptionadjustmentmethod_trial_internal'), (b'accounting', '0029_merge'), (b'accounting', '0030_remove_softwareplan_visibility_trial_internal'), (b'accounting', '0031_credit_line_feature_type_blank'), (b'accounting', '0031_create_report_builder_roles'), (b'accounting', '0032_merge'), (b'accounting', '0027_more_prbac_bootstrap'), (b'accounting', '0031_merge'), (b'accounting', '0033_merge'), (b'accounting', '0034_do_not_email_reminders'), (b'accounting', '0035_kill_date_received'), (b'accounting', '0036_subscription_skip_invoicing_if_no_feature_charges'), (b'accounting', '0037_assign_explicit_community_subscriptions'), (b'accounting', '0038_bootstrap_new_user_buckets'), (b'accounting', '0039_auto_20160829_0828'), (b'accounting', '0040_community_v1'), (b'accounting', '0041_grandfather_export_privs'), (b'accounting', '0042_bootstrap_prbac_roles'), (b'accounting', '0043_bootstrap_location_restrictions'), (b'accounting', '0044_subscription_skip_auto_downgrade'), (b'accounting', '0045_dimagi_contact_email_field'), (b'accounting', '0046_created_by_blank'), (b'accounting', '0047_ensure_default_product_plans'), (b'accounting', '0048_remove_defaultproductplan_product_type'), (b'accounting', '0049_update_user_buckets'), (b'accounting', '0050_fix_product_rates'), (b'accounting', '0051_add_report_builder_flag'), (b'accounting', '0052_ensure_report_builder_plans')]

    initial = True

    dependencies = [
        ('django_prbac', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('salesforce_account_id', models.CharField(blank=True, db_index=True, help_text=b'This is how we link to the salesforce account', max_length=80, null=True)),
                ('created_by', models.CharField(blank=True, max_length=80)),
                ('created_by_domain', models.CharField(blank=True, max_length=256, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('dimagi_contact', models.EmailField(blank=True, max_length=254)),
                ('is_auto_invoiceable', models.BooleanField(default=False)),
                ('date_confirmed_extra_charges', models.DateTimeField(blank=True, null=True)),
                ('account_type', models.CharField(choices=[(b'CONTRACT', b'Created by contract'), (b'USER_CREATED', b'Created by user'), (b'GLOBAL_SERVICES', b'Created by Global Services'), (b'INVOICE_GENERATED', b'Generated by an invoice'), (b'TRIAL', b'Is trial account')], default=b'CONTRACT', max_length=25)),
                ('is_active', models.BooleanField(default=True)),
                ('entry_point', models.CharField(choices=[(b'CONTRACTED', b'Contracted'), (b'SELF_STARTED', b'Self-started'), (b'NOT_SET', b'Not Set')], default=b'NOT_SET', max_length=25)),
                ('auto_pay_user', models.CharField(blank=True, max_length=80, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('last_payment_method', models.CharField(choices=[(b'CC_ONE_TIME', b'Credit Card - One Time'), (b'CC_AUTO', b'Credit Card - Autopay'), (b'WIRE', b'Wire'), (b'ACH', b'ACH'), (b'OTHER', b'Other'), (b'BU_PAYMENT', b'Payment to local BU'), (b'NONE', b'None')], default=b'NONE', max_length=25)),
                ('pre_or_post_pay', models.CharField(choices=[(b'PREPAY', b'Prepay'), (b'POSTPAY', b'Postpay'), (b'NOT_SET', b'Not Set')], default=b'NOT_SET', max_length=25)),
            ],
            bases=(corehq.util.mixin.ValidateModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BillingRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('emailed_to', models.CharField(db_index=True, max_length=254)),
                ('skipped_email', models.BooleanField(default=False)),
                ('pdf_data_id', models.CharField(max_length=48)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CreditAdjustment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[(b'MANUAL', b'manual'), (b'SALESFORCE', b'via Salesforce'), (b'INVOICE', b'invoice generated'), (b'LINE_ITEM', b'line item generated'), (b'TRANSFER', b'transfer from another credit line'), (b'DIRECT_PAYMENT', b'payment from client received')], default=b'MANUAL', max_length=25)),
                ('note', models.TextField(blank=True)),
                ('amount', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('web_user', models.CharField(blank=True, max_length=80, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            bases=(corehq.util.mixin.ValidateModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CreditLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(blank=True, choices=[(b'', b'')], max_length=25, null=True)),
                ('feature_type', models.CharField(blank=True, choices=[(b'User', b'User'), (b'SMS', b'SMS')], max_length=10, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('balance', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            bases=(corehq.util.mixin.ValidateModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(db_index=True, max_length=25)),
                ('symbol', models.CharField(max_length=10)),
                ('rate_to_default', models.DecimalField(decimal_places=9, default=Decimal('1.0'), max_digits=20)),
                ('date_updated', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='DefaultProductPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edition', models.CharField(choices=[(b'Community', b'Community'), (b'Standard', b'Standard'), (b'Pro', b'Pro'), (b'Advanced', b'Advanced'), (b'Enterprise', b'Enterprise'), (b'Reseller', b'Reseller'), (b'Managed Hosting', b'Managed Hosting')], default=b'Community', max_length=25)),
                ('is_trial', models.BooleanField(default=False)),
                ('is_report_builder_enabled', models.BooleanField(default=False)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('feature_type', models.CharField(choices=[(b'User', b'User'), (b'SMS', b'SMS')], db_index=True, max_length=10)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeatureRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name=b'Monthly Fee')),
                ('monthly_limit', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(2147483647), django.core.validators.MinValueValidator(-2147483648)], verbose_name=b'Monthly Included Limit')),
                ('per_excess_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name=b'Fee Per Excess of Limit')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Feature')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('tax_rate', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('balance', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('date_due', models.DateField(db_index=True, null=True)),
                ('date_paid', models.DateField(blank=True, null=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('is_hidden_to_ops', models.BooleanField(default=False)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_description', models.TextField(blank=True, null=True)),
                ('base_cost', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('unit_description', models.TextField(blank=True, null=True)),
                ('unit_cost', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('quantity', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(2147483647), django.core.validators.MinValueValidator(-2147483648)])),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('feature_rate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.FeatureRate')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('web_user', models.CharField(db_index=True, max_length=80, null=True)),
                ('method_type', models.CharField(choices=[(b'Stripe', b'Stripe')], db_index=True, default=b'Stripe', max_length=50)),
                ('customer_id', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('transaction_id', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.PaymentMethod')),
            ],
        ),
        migrations.CreateModel(
            name='SoftwarePlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
                ('description', models.TextField(blank=True, help_text=b'If the visibility is INTERNAL, this description field will be used.')),
                ('edition', models.CharField(choices=[(b'Community', b'Community'), (b'Standard', b'Standard'), (b'Pro', b'Pro'), (b'Advanced', b'Advanced'), (b'Enterprise', b'Enterprise'), (b'Reseller', b'Reseller'), (b'Managed Hosting', b'Managed Hosting')], default=b'Enterprise', max_length=25)),
                ('visibility', models.CharField(choices=[(b'PUBLIC', b'Anyone can subscribe'), (b'INTERNAL', b'Dimagi must create subscription'), (b'TRIAL', b'This is a Trial Plan')], default=b'INTERNAL', max_length=10)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SoftwarePlanVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('feature_rates', models.ManyToManyField(blank=True, to='accounting.FeatureRate')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.SoftwarePlan')),
            ],
        ),
        migrations.CreateModel(
            name='SoftwareProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('product_type', models.CharField(choices=[(b'CommCare', b'CommCare'), (b'CommTrack', b'CommTrack'), (b'CommConnect', b'CommConnect')], db_index=True, max_length=25)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SoftwareProductRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.SoftwareProduct')),
            ],
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=256, unique=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salesforce_contract_id', models.CharField(blank=True, max_length=80, null=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField(blank=True, null=True)),
                ('date_delay_invoicing', models.DateField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False)),
                ('do_not_invoice', models.BooleanField(default=False)),
                ('no_invoice_reason', models.CharField(blank=True, max_length=256, null=True)),
                ('do_not_email_invoice', models.BooleanField(default=False)),
                ('do_not_email_reminder', models.BooleanField(default=False)),
                ('auto_generate_credits', models.BooleanField(default=False)),
                ('is_trial', models.BooleanField(default=False)),
                ('skip_invoicing_if_no_feature_charges', models.BooleanField(default=False)),
                ('service_type', models.CharField(choices=[(b'IMPLEMENTATION', b'Implementation'), (b'PRODUCT', b'Product'), (b'TRIAL', b'Trial'), (b'EXTENDED_TRIAL', b'Extended Trial'), (b'SANDBOX', b'Sandbox'), (b'INTERNAL', b'Internal')], default=b'NOT_SET', max_length=25)),
                ('pro_bono_status', models.CharField(choices=[(b'FULL_PRICE', b'Full Price'), (b'DISCOUNTED', b'Discounted'), (b'PRO_BONO', b'Pro Bono')], default=b'FULL_PRICE', max_length=25)),
                ('funding_source', models.CharField(choices=[(b'DIMAGI', b'Dimagi'), (b'CLIENT', b'Client Funding'), (b'EXTERNAL', b'External Funding')], default=b'CLIENT', max_length=25)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('is_hidden_to_ops', models.BooleanField(default=False)),
                ('skip_auto_downgrade', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionAdjustment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[(b'CREATE', b'A new subscription created from scratch.'), (b'MODIFY', b'Some part of the subscription was modified...likely a date.'), (b'CANCEL', b'The subscription was cancelled with no followup subscription.'), (b'UPGRADE', b'The subscription was upgraded to the related subscription.'), (b'DOWNGRADE', b'The subscription was downgraded to the related subscription.'), (b'SWITCH', b'The plan was changed to the related subscription and was neither an upgrade or downgrade.'), (b'REACTIVATE', b'The subscription was reactivated.'), (b'RENEW', b'The subscription was renewed.')], default=b'CREATE', max_length=50)),
                ('method', models.CharField(choices=[(b'USER', b'User'), (b'INTERNAL', b'Ops'), (b'TASK', b'Task (Invoicing)'), (b'TRIAL', b'30 Day Trial')], default=b'INTERNAL', max_length=50)),
                ('note', models.TextField(null=True)),
                ('web_user', models.CharField(max_length=80, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('new_date_start', models.DateField()),
                ('new_date_end', models.DateField(blank=True, null=True)),
                ('new_date_delay_invoicing', models.DateField(blank=True, null=True)),
                ('new_salesforce_contract_id', models.CharField(blank=True, max_length=80, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('invoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.Invoice')),
                ('related_subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subscriptionadjustment_related', to='accounting.Subscription')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Subscription')),
            ],
        ),
        migrations.CreateModel(
            name='WireBillingRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('emailed_to', models.CharField(db_index=True, max_length=254)),
                ('skipped_email', models.BooleanField(default=False)),
                ('pdf_data_id', models.CharField(max_length=48)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='WireInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('tax_rate', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('balance', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10)),
                ('date_due', models.DateField(db_index=True, null=True)),
                ('date_paid', models.DateField(blank=True, null=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('is_hidden_to_ops', models.BooleanField(default=False)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('domain', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BillingContactInfo',
            fields=[
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='accounting.BillingAccount')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Last Name')),
                ('email_list', jsonfield.fields.JSONField(default=list, help_text='We will email communications regarding your account to the emails specified here.', verbose_name='Contact Emails')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number')),
                ('company_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Company / Organization')),
                ('first_line', models.CharField(max_length=50, verbose_name='Address First Line')),
                ('second_line', models.CharField(blank=True, max_length=50, null=True, verbose_name='Address Second Line')),
                ('city', models.CharField(max_length=50, verbose_name='City')),
                ('state_province_region', models.CharField(max_length=50, verbose_name='State / Province / Region')),
                ('postal_code', models.CharField(max_length=20, verbose_name='Postal Code')),
                ('country', models.CharField(max_length=50, verbose_name='Country')),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='wirebillingrecord',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.WireInvoice'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.BillingAccount'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='plan_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.SoftwarePlanVersion'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Subscriber'),
        ),
        migrations.AddField(
            model_name='softwareplanversion',
            name='product_rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.SoftwareProductRate'),
        ),
        migrations.AddField(
            model_name='softwareplanversion',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_prbac.Role'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='product_rate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.SoftwareProductRate'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Subscription'),
        ),
        migrations.AddField(
            model_name='defaultproductplan',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.SoftwarePlan'),
        ),
        migrations.AddField(
            model_name='creditline',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.BillingAccount'),
        ),
        migrations.AddField(
            model_name='creditline',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.Subscription'),
        ),
        migrations.AddField(
            model_name='creditadjustment',
            name='credit_line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.CreditLine'),
        ),
        migrations.AddField(
            model_name='creditadjustment',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.Invoice'),
        ),
        migrations.AddField(
            model_name='creditadjustment',
            name='line_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.LineItem'),
        ),
        migrations.AddField(
            model_name='creditadjustment',
            name='payment_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.PaymentRecord'),
        ),
        migrations.AddField(
            model_name='creditadjustment',
            name='related_credit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='creditadjustment_related', to='accounting.CreditLine'),
        ),
        migrations.AddField(
            model_name='billingrecord',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Invoice'),
        ),
        migrations.AddField(
            model_name='billingaccount',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounting.Currency'),
        ),
        migrations.CreateModel(
            name='StripePaymentMethod',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('accounting.paymentmethod',),
        ),
        migrations.CreateModel(
            name='WirePrepaymentBillingRecord',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('accounting.wirebillingrecord',),
        ),
        migrations.CreateModel(
            name='WirePrepaymentInvoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('accounting.wireinvoice',),
        ),
        migrations.AlterUniqueTogether(
            name='defaultproductplan',
            unique_together=set([('edition', 'is_trial', 'is_report_builder_enabled')]),
        ),
    ] + [
        HqRunPython(cchq_prbac_bootstrap),
        HqRunPython(_cchq_software_plan_bootstrap),
    ]
