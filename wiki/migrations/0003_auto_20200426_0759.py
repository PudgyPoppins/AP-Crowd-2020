# Generated by Django 3.0.5 on 2020-04-26 07:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wiki', '0002_auto_20200424_0513'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportReasons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['title']},
        ),
        migrations.AlterField(
            model_name='page',
            name='protection',
            field=models.CharField(choices=[('NO', 'None'), ('LO', 'Locked'), ('NC', "Locked and doesn't allow children"), ('CO', 'Confirmed users only')], default='NO', help_text="Setting the protection to 'locked' will not allow others to edit this page in the future.", max_length=2),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason_text', models.CharField(blank=True, help_text='Please consider elaborating more on the reason for this report.', max_length=500, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('reason', models.ManyToManyField(to='wiki.ReportReasons')),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='wiki.Revision')),
            ],
        ),
    ]
