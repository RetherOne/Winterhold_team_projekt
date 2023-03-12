# Generated by Django 4.0.1 on 2022-02-19 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0011_armor_part'),
    ]

    operations = [
        migrations.AlterField(
            model_name='armor',
            name='part',
            field=models.CharField(blank=True, choices=[('helmet', 'Шлем'), ('chestplate', 'Нагрудник'), ('leggings', 'Поножи'), ('boots', 'Ботинки')], max_length=30),
        ),
    ]