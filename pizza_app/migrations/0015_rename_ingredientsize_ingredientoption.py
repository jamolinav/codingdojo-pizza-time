# Generated by Django 3.2.3 on 2021-06-12 15:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pizza_app', '0014_auto_20210612_1546'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IngredientSize',
            new_name='IngredientOption',
        ),
    ]
