# Generated by Django 2.2 on 2019-05-25 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0011_auto_20190515_1656'),
    ]

    operations = [
        migrations.CreateModel(
            name='comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(default='', max_length=20)),
                ('content', models.TextField(default='', max_length=5000)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
