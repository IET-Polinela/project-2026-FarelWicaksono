from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_report_reporter_and_draft_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-updated_at', '-id']},
        ),
    ]
