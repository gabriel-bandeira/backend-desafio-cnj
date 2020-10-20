# Generated by Django 3.1.2 on 2020-10-19 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0004_auto_20201018_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='method',
            field=models.TextField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='court',
            field=models.TextField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='court_class',
            field=models.TextField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='judging_body',
            field=models.TextField(default=None, max_length=255, null=True),
        ),
    ]