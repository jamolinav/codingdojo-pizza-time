# Generated by Django 3.2.3 on 2021-06-12 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pizza_app', '0013_auto_20210612_1542'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredientsize',
            name='multiple_option',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='multiple_option',
            field=models.BooleanField(default=False),
        ),
    ]
