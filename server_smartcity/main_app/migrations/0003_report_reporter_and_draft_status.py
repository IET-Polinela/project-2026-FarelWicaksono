from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def normalize_in_progress(apps, schema_editor):
    Report = apps.get_model('main_app', 'Report')
    Report.objects.filter(status='IN PROGRESS').update(status='IN_PROGRESS')


def restore_in_progress(apps, schema_editor):
    Report = apps.get_model('main_app', 'Report')
    Report.objects.filter(status='IN_PROGRESS').update(status='IN PROGRESS')


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main_app', '0002_alter_report_id_alter_report_status'),
    ]

    operations = [
        migrations.RunPython(normalize_in_progress, restore_in_progress),
        migrations.AddField(
            model_name='report',
            name='reporter',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reports',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(
                choices=[
                    ('DRAFT', 'Draft'),
                    ('REPORTED', 'Reported'),
                    ('VERIFIED', 'Verified'),
                    ('IN_PROGRESS', 'In Progress'),
                    ('RESOLVED', 'Resolved'),
                ],
                default='DRAFT',
                max_length=20,
            ),
        ),
    ]
