# Generated by Django 2.2.1 on 2019-06-26 01:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0012_sent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inbox',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='sent',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='starred',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='trash',
            options={'ordering': ['-created_at']},
        ),
    ]
