# Generated by Django 2.2.10 on 2020-03-25 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20200324_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(default='empty', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='firstName',
            field=models.CharField(default='empty', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='lastName',
            field=models.CharField(default='empty', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=40),
        ),
    ]
