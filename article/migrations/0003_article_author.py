# Generated by Django 2.2 on 2019-05-10 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.CharField(default='', max_length=20),
        ),
    ]