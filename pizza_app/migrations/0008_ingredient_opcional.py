# Generated by Django 3.2.3 on 2021-06-12 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pizza_app', '0007_remove_ingredientsize_type_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='opcional',
            field=models.BooleanField(default=False),
        ),
    ]
