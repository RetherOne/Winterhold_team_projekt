from math import radians
import re
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import redirect, render

import shelve
from random import choice, randint
from icecream import ic

from Game.models import Enemy, Food, Hint, Place, Armor, Weapon
from .game_classes import Character, antigod_mode_stats, buy, change_place, eat_food, god_mode_stats, roll, pack, unpack,  \
    atack, dodge, check, equip_item, check_enemy, update_stat
from Winterhold.settings import STAT_TRANSLATION

#Views 
def start_page(request:HttpRequest):
    if request.user.is_authenticated:
        return redirect("Game:travel")
    return render(request, 'Game/start_page.html')
 
@login_required
def new_game_page(request):
    return render(request, 'Game/new_game.html')

@login_required
def new_game(request):
    user=str(request.user.pk)
    pack(user, 'ch', Character())
    return redirect('Game:greetings')

@login_required
def greet(request):
    user=str(request.user.pk)
    if user in shelve.open(f'ch_files/{user}').keys():
        return redirect("Game:travel")
    else:
        pack(user, 'ch', Character())
    
    return render(request, 'Game/greetings.html', context={"ch":unpack(str(request.user.pk), 'ch')})

@login_required
def travel(request:HttpRequest):
    
    user=str(request.user.pk)
    ch=unpack(user, 'ch')
     
    msg=ch.place.msg

    if request.method == 'POST':
            
        msg, coords_changed=change_place(request, ch)

        if ch.place.is_first_enter and coords_changed and not ch.is_god:
            pack(user, 'ch', ch)
            return redirect('Game:travel_page')

    if check_enemy(ch):
        pack(user, 'ch', ch)
        return redirect("Game:fight")
    
    pack(user, 'ch', ch)
    context={'ch':ch, 'msg':msg}
    return render(request, 'Game/travel.html', context)

@login_required
def travel_page(request:HttpRequest):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')
    
    ch.place.is_first_enter=False
    
    pack(user, 'ch', ch)
    context={'ch':ch}
    return render(request, 'Game/travel_page.html', context)

@login_required
def fight(request):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')

    if not ch.enemy:
        return redirect("Game:travel")

    atack_msg=atack(request, ch)

    if atack_msg=='run':
        pack(user, 'ch', ch)
        return redirect("Game:travel")

    dodge_msg=dodge(request, ch)

    pack(user, 'ch', ch)
    return render(request, *check(user, ch, atack_msg, dodge_msg))


@login_required
def shop(request:HttpRequest, place):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')
    msg=''
    
    if ch.place.name!=place:
        raise Http404
        
    if request.method=='POST':
        msg=buy(request, ch)
    else:
        msg='Добро пожаловать'

    if place=='Кузня':
        goods=list(Armor.objects.exclude(name__in=ch.inventory).order_by('price')) + list(Weapon.objects.exclude(name__in=ch.inventory).order_by('price'))
    elif place=='Таверна':
        goods=Food.objects.all()

    pack(user, 'ch', ch)
    context={'goods':goods, 'ch':ch, 'msg':msg}
    return render(request, 'Game/shop.html', context)

@login_required
def rest(request:HttpRequest):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')

    if check_enemy(ch):
        raise Http404

    return render(request, 'Game/rest.html', {'ch':ch})
    
@login_required
def equip(request:HttpRequest):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')

    if check_enemy(ch):
        raise Http404

    msg=''
    if request.method=='POST':
        msg=equip_item(request, ch)
    
    inventory=list(filter(lambda item:item.section in ('Armor', 'Weapon') and item not in (ch.weapon, ch.helmet, ch.chestplate, ch.leggings, ch.boots), ch.inventory))
    context={'inventory':inventory, 'msg':msg, 'ch':ch}
    pack(user, 'ch', ch)
    return render(request, 'Game/equipment.html', context)

@login_required
def stat_update(request:HttpRequest):
    user = str(request.user.pk)
    ch = unpack(user, 'ch')
    
    if check_enemy(ch):
        raise Http404

    msg = 'Что желаете улучшить?'
    
    if request.method == 'POST':
        msg = update_stat(ch, request.POST['update'])
    
    pack(user, 'ch', ch)
    context = {'point_translation':STAT_TRANSLATION, 'ch':ch, 'msg':msg}
    return render(request, 'Game/stat_update.html', context)

@login_required
def eat(request:HttpRequest):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')

    if check_enemy(ch):
        raise Http404

    if request.method=='POST':
        eat_food(request.POST['eat'], ch)

    food = {f.name:ch.inventory.count(f) for f in set(filter(lambda item: item.section=='Food', ch.inventory))}
    context={'food':food, 'ch':ch}

    pack(user, 'ch', ch)
    return render(request, 'Game/eat.html', context)

@login_required
def show_hint(request:HttpRequest):
    user=str(request.user.pk)
    ch=unpack(user, 'ch')

    if ch.place.name!='Таверна':
        raise Http404

    hints=Hint.objects.exclude(pk__in=ch.hints)

    if not hints:
        text='Мне больше нечего тебе сказать, странник'
    else:
        hint=hints[randint(0, len(hints)-1)]
        text=hint.text
        ch.hints.append(hint.pk)

    pack(user, 'ch', ch)
    context={'hint':text, 'ch':ch}
    return render(request, 'Game/hint.html', context)

@login_required
def finish_game(request:HttpRequest):
    ch=unpack(str(request.user.pk), 'ch')

    if ch.map['Руины'].enemy.alive:
        raise Http404
    
    return render(request, 'Game/finish_game.html')

@login_required
def gode_mode(request:HttpRequest):
    user=str(request.user.pk)

    if not request.user.is_superuser:
        raise Http404
    
    ch=unpack(user, 'ch')
    god_mode_stats(ch)
    pack(user, 'ch', ch)
    return redirect("Game:travel")

@login_required
def antigod_mode(request:HttpRequest):
    user=str(request.user.pk)

    if not request.user.is_superuser:
        raise Http404

    ch=unpack(user, 'ch')
    antigod_mode_stats(ch)
    pack(user, 'ch', ch)
    return redirect("Game:travel")