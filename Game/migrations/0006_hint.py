# Generated by Django 4.0.1 on 2022-02-05 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0005_enemy_seal_place_first_enter_text_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
    ]
