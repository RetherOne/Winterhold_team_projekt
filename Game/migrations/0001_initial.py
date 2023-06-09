# Generated by Django 4.0.1 on 2022-01-25 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Armor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('price', models.IntegerField()),
                ('protection', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Enemy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=21)),
                ('damage', models.IntegerField()),
                ('hp', models.IntegerField(null=True)),
                ('alive', models.BooleanField(default=True)),
                ('reward', models.IntegerField(null=True)),
                ('msg', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('price', models.IntegerField()),
                ('damage', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('name', models.CharField(max_length=20)),
                ('msg', models.TextField()),
                ('is_shop', models.BooleanField(default=False)),
                ('enemy', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='Game.enemy')),
            ],
        ),
    ]
