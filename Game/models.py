from multiprocessing import Condition
from random import choices
from statistics import mode
from django.db import models
from django.db.models.deletion import PROTECT
from django.forms import IntegerField, Textarea

# Create your models here.

class Enemy(models.Model):
    name=models.CharField(max_length=21)
    damage=models.IntegerField()
    hp=models.IntegerField(null=True)
    alive=models.BooleanField(default=True)
    reward=models.IntegerField(null=True)
    exp = models.IntegerField(default=0)
    msg=models.TextField()
    seal=models.CharField(max_length=30, blank=True)
    death_message=models.TextField(null=True)

    def __str__(self) -> str:
        return self.name

class Place(models.Model):
    x=models.IntegerField(blank=False)
    y=models.IntegerField(blank=False)
    subloc_pk = models.IntegerField(default=0)
    name=models.CharField(max_length=20)
    msg=models.TextField()
    enemy=models.ForeignKey(Enemy, on_delete=PROTECT, blank=True, null=True)
    not_allowed_direction=models.CharField(max_length=100, blank=True)
    transition = models.BooleanField(default = False)
    is_shop=models.BooleanField(default=False)
    is_rest_place=models.BooleanField(default=True)
    is_first_enter=models.BooleanField(default=True)
    first_enter_text=models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

class Armor(models.Model):
    parts=[
        ('helmet','Шлем'),
        ('chestplate','Нагрудник'),
        ('leggings','Поножи'),
        ('boots','Ботинки')
    ]

    name=models.CharField(max_length=40)
    price=models.IntegerField()
    protection=models.IntegerField()
    level = models.IntegerField(default = 1)
    section=models.CharField(max_length=30, default='Armor')
    part=models.CharField(choices=parts,max_length=30,blank=True)
    dexterity=models.IntegerField(default = 0)

    def __str__(self):
        return self.name

class Weapon(models.Model):
    name=models.CharField(max_length=40)
    price=models.IntegerField()
    damage=models.IntegerField()
    level = models.IntegerField(default = 1)
    section=models.CharField(max_length=30, default='Weapon')
    crit_add=models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Food(models.Model):
    name=models.CharField(max_length=50)
    price=models.IntegerField()
    satiety=models.IntegerField()
    section=models.CharField(max_length=50, default='Food')

    def __str__(self):
        return self.name

class Hint(models.Model):
    text=models.TextField()

    def __str__(self):
        return ' '.join(self.text.split()[:5])