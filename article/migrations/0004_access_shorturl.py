# Generated by Django 2.2 on 2019-05-11 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_article_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='access',
            name='shorturl',
            field=models.CharField(default='', max_length=10),
        ),
    ]