# Generated by Django 2.2.20 on 2021-05-07 14:55

import dimagi.utils.couch.migration
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_hqapikey_domain'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleAssignableBy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow_all', models.BooleanField(default=True)),
                ('allowed_items', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), blank=True, null=True, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='SQLPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SQLUserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=128, null=True)),
                ('name', models.CharField(max_length=128, null=True)),
                ('default_landing_page', models.CharField(choices=[('dashboard', 'Dashboard'), ('webapps', 'Web Apps'), ('reports', 'Reports'), ('downloads', 'Data File Downloads')], max_length=64, null=True)),
                ('is_non_admin_editable', models.BooleanField(default=False)),
                ('is_archived', models.BooleanField(default=False)),
                ('upstream_id', models.CharField(max_length=32, null=True)),
                ('couch_id', models.CharField(max_length=126, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'users_userrole',
            },
            bases=(dimagi.utils.couch.migration.SyncSQLToCouchMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name='sqluserrole',
            index=models.Index(fields=['domain'], name='users_userr_domain_c07a58_idx'),
        ),
        migrations.AddIndex(
            model_name='sqluserrole',
            index=models.Index(fields=['couch_id'], name='users_userr_couch_i_a40af7_idx'),
        ),
        migrations.AddField(
            model_name='rolepermission',
            name='permission_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.SQLPermission'),
        ),
        migrations.AddField(
            model_name='rolepermission',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.SQLUserRole'),
        ),
        migrations.AddField(
            model_name='roleassignableby',
            name='assignable_by_role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='can_assign_roles', to='users.SQLUserRole'),
        ),
        migrations.AddField(
            model_name='roleassignableby',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.SQLUserRole'),
        ),
    ]
