from django.contrib import admin

from Game.models import Armor, Enemy, Food, Hint, Place, Weapon

# Register your models here.
admin.site.register(Place)
admin.site.register(Enemy)
admin.site.register(Weapon)
admin.site.register(Armor)
admin.site.register(Food)
admin.site.register(Hint)