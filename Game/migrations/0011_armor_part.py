# Generated by Django 4.0.1 on 2022-02-19 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0010_enemy_death_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='armor',
            name='part',
            field=models.CharField(blank=True, choices=[('Шлем', 'Шлем'), ('Нагрудник', 'Нагрудник'), ('Поножи', 'Поножи'), ('Ботики', 'Ботинки')], max_length=30),
        ),
    ]
