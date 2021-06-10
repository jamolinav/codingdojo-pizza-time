# Generated by Django 3.2.3 on 2021-06-10 00:07

from django.db import migrations, models
import django.db.models.deletion
import pizza_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Extra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
                ('price', models.IntegerField()),
                ('discount', models.BooleanField(default=False)),
                ('special_price', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PizzaSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
                ('type', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
                ('last_name', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_users', to='pizza_app.usertype')),
            ],
        ),
        migrations.CreateModel(
            name='Pizza',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, validators=[pizza_app.models.ValidarLongitudMinima])),
                ('price', models.IntegerField()),
                ('discount', models.BooleanField(default=False)),
                ('special_price', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('all_ingredients', models.ManyToManyField(related_name='all_in_pizzas', to='pizza_app.Ingredient')),
                ('all_users_like', models.ManyToManyField(related_name='favorites_pizzas', to='pizza_app.User')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_pizzas_size', to='pizza_app.pizzasize')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_pizzas', to='pizza_app.user')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorite', models.BooleanField(default=False)),
                ('total', models.IntegerField()),
                ('total_discount', models.IntegerField()),
                ('fee_delvery', models.IntegerField()),
                ('tax', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_orders', to='pizza_app.user')),
            ],
        ),
        migrations.CreateModel(
            name='DetailPizzaOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('all_pizzas', models.ManyToManyField(related_name='all_pizzas_in_orders', to='pizza_app.Pizza')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_pizzas_order', to='pizza_app.user')),
            ],
        ),
        migrations.CreateModel(
            name='DetailExtraOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('all_extras', models.ManyToManyField(related_name='all_exras_in_orders', to='pizza_app.Pizza')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_extras_order', to='pizza_app.user')),
            ],
        ),
    ]
