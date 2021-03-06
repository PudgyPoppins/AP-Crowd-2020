# Generated by Django 3.0.5 on 2020-04-28 20:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wiki', '0004_auto_20200426_0806'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReportReasons',
            new_name='ReportReason',
        ),
        migrations.AlterModelOptions(
            name='revision',
            options={'ordering': ['-current', 'created_date']},
        ),
        migrations.AddField(
            model_name='report',
            name='revision_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='revision_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
