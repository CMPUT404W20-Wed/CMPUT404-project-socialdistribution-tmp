# Generated by Django 2.2.10 on 2020-03-13 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_merge_20200313_1603'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['published']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-published']},
        ),
    ]
