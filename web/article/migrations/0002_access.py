# Generated by Django 2.2 on 2019-05-10 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='access',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=100)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
