from django.db.models import Q
from logging.config import valid_ident
from math import ceil
from .models import Place, Armor, Weapon, Food
from random import randint, choice
from icecream import ic
import shelve
from Winterhold.settings import DIRECTION_DEPENDENCIES, LEVEL_DEPENDENCIES, MAX_LEVEL, STATLEVEL_DEPENDENCIES, MAX_STAT_LEVEL

class Character():
    def __init__(self):
        self.hp=100
        self.max_hp=100
        self.damage=10
        self.x=0
        self.y=0
        self.sublocation_pk = 0
        self.enemy=None
        self.coins=100
        self.last=[0,0]
        self.weapon=None
        self.helmet=None
        self.chestplate=None
        self.leggings=None
        self.boots=None
        self.exp = 0
        self.level = 1
        self.lvl_points = 1
        self.dexterity = 0
        self.accurate = 0
        self.crit_chance = 10
        self.next_lvl = LEVEL_DEPENDENCIES[self.level+1]
        self.place=Place.objects.get(x=0, y=0)
        self.inventory=[]
        self.seals=[]
        self.hints=[]
        self.allocated_points = {'hp':0, 'damage':0, 'dexterity':0, 'accurate':0, 'crit_chance':0}
        self.map={place.name:place for place in Place.objects.all()}
        self.is_god = False
        
    def load(self, stats):
        self.__dict__.update(stats)

    def stat_check(self):
        if self.hp>self.max_hp:
            self.hp=self.max_hp
    
def eat_food(food, ch):
    food=Food.objects.get(name=food)
    ch.hp+=food.satiety
    ch.inventory.remove(food)
    ch.stat_check()

def update_stat(ch, stat):
    value = STATLEVEL_DEPENDENCIES[stat]

    if ch.allocated_points[stat] == MAX_STAT_LEVEL:
        return 'Вы достигли своего предела в этом'

    if ch.lvl_points == 0:
        return 'Вам не хватает опыта'

    if stat == 'hp':
        ch.max_hp += value
        
    exec(f'ch.{stat} += {value}')
    
    ch.allocated_points[stat] += 1
    ch.lvl_points -= 1

    return 'Вы успешно улучшили свое тело'

def check_enemy(ch):
    enemy=ch.map[ch.place.name].enemy
    if enemy and enemy.alive:
        ch.enemy=enemy
        return True
    return False

def buy(request, ch):
    name, section = request.POST['buy'].split(',')
    item = eval(f'{section}.objects.get(name="{name}")')
    if ch.coins >= item.price:
        ch.inventory.append(item)
        ch.coins -= item.price
        msg = f'Вы купили {item}'
    else:
        msg = 'У вас недостаточно денег'
    return msg

def roll(c):
    if randint(0, 100)<=c:
        return True
    return False

def pack(shelve_name, key, value) -> None:
    with shelve.open(f'ch_files/{shelve_name}') as user_shelve:
        user_shelve[key]=value

def unpack(shelve_name, key):
    with shelve.open(f'ch_files/{shelve_name}') as user_shelve:
        return user_shelve[key]

def place_conditional(ch, x, y):
    place=Place.objects.get(x=ch.x+x, y=ch.y+y, subloc_pk=ch.sublocation_pk)

    if place.name=='Руины' and len(ch.seals)!=4:
        msg='Ворота не открываются'
        return False, msg

    if place.name in ch.place.not_allowed_direction:
        return False, 'Тут стена'

    return True, ''   

def enter(ch):
    if ch.sublocation_pk != 0:
        ch.sublocation_pk = 0
    else:
        ch.sublocation_pk = Place.objects.filter(x = ch.x, y = ch.y).exclude(subloc_pk = 0)[0].subloc_pk
    
def change_place(request, ch):
    if request.POST['direction'] == 'go_into':
        enter(ch)
        x, y = 0, 0
    else:
        x, y = DIRECTION_DEPENDENCIES[request.POST['direction']]
    coords_changed = False

    if Place.objects.filter(x=ch.x+x, y=ch.y+y, subloc_pk = ch.sublocation_pk):
        allowed, msg = place_conditional(ch, x, y)
        if allowed:
            ch.last = [ch.x, ch.y]
            ch.x += x
            ch.y += y
            coords_changed = True
            ch.place=ch.map[Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk).name]
            msg=ch.place.msg
    else:
        msg='Вы не можете пройти дальше'
    return msg, coords_changed

def run_actions(ch):
    ch.enemy.hp=Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk).enemy.hp
    ch.enemy.damage=Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk).enemy.damage
    ch.enemy=None
    ch.x, ch.y=ch.last
    ch.place=Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk)

def check_part(part, ch):
    damage=ch.damage
    crit = False
    if part=='head' and roll(60+ch.accurate):
        damage*=2
        msg=f'Вы попали в голову'
    elif part=='body' and roll(80+ch.accurate):
        msg=f'Вы попали по корпусу'
    elif part=='limbs' and roll(60+ch.accurate):    
        msg='Вы попали по '+choice(['руке', 'ноге'])
        ch.enemy.damage=ceil(ch.enemy.damage*0.8)
    elif part=='run':
        run_actions(ch)
        return ('run', 0, False)
    else:
        damage=0
        msg='Вы промахнулись'

    if roll(ch.crit_chance) and damage != 0:
        damage*=1.5
        crit = True

    return (msg, damage, crit)

def atack(request, ch):
    damage=ch.damage
    msg=''
    if request.method=='POST':
        msg, damage, crit=check_part(request.POST['atack'], ch)

        if damage!=0:
            msg+=f', нанеся {int(damage)} ед урона'
            if crit:
                msg+=', попав в уязвимое место'
            ch.enemy.hp-=damage 
            
        return msg

    else:
        return ch.enemy.msg

def dodge(request, ch):
    msg=''
    if request.method=="POST":
        if roll(25+ch.dexterity):
            msg='Вы увернулись'
        else:
            ch.hp-=ch.enemy.damage
            msg=f'Противник смог нанести удар, нанеся {int(ch.enemy.damage)} урона'
    return msg

def check_final_boss(ch):
    if ch.enemy.name=='Бог тьмы':
        template='Game/finish_game.html'
    else:
        template='Game/win.html'
    return template

def lose_actions(ch):
    ch.enemy.hp=Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk).enemy.hp
    ch.enemy.damage=Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk).enemy.damage

    ch.enemy=None
    ch.x, ch.y=0,0

    if ch.coins>=45:
        ch.coins-=45
        ch.hp=ch.max_hp
        msg='Оплатив лечение, вы вышли замка'
    else:
        msg='Вы открываете глаза в замке, все тело болит'
        ch.hp=10+ch.coins*2
        ch.coins=0
        ch.stat_check()

    return ('Game/lose.html', {'msg':msg, 'ch':ch})

def check_level(ch):

    while ch.level != 15 and ch.exp >= ch.next_lvl:
        ch.exp = ch.exp - ch.next_lvl
        ch.level += 1
        ch.lvl_points += 1
        ch.hp = ch.max_hp
        ch.next_lvl = LEVEL_DEPENDENCIES[ch.level+1]
    
        if ch.level >= MAX_LEVEL:
            ch.level = MAX_LEVEL
            ch.exp = 'max'

def win_actions(ch):

    if ch.hp<=0:
        ch.hp+=ch.enemy.damage

    ch.map[ch.place.name].enemy.alive=False
    ch.coins+=ch.enemy.reward

    if ch.next_lvl != 'max':
        ch.exp += ch.enemy.exp
        check_level(ch)
    msg=f'Враг повержен, вы получили {ch.enemy.reward} монет и {ch.enemy.exp} опыта'
    
    if ch.enemy.seal:
        ch.seals.append(ch.enemy.seal)
        msg+=f' и {ch.enemy.seal}'
        ch.x, ch.y=0, 0

    template=check_final_boss(ch)
    rend=(template, {'msg':msg, 'dmsg':ch.enemy.death_message})
    ch.enemy=None
    return rend

def check(user, ch, atack_msg, dodge_msg):
    if ch.enemy.hp<=0:
        rend=win_actions(ch)
        
    elif ch.hp<=0:
        rend=lose_actions(ch)
    else:
        context={'enemy':ch.enemy, 'ch':ch, 'enemy_max_hp':ch.place.enemy.hp, 'atack_msg':atack_msg, 'dodge_msg':dodge_msg}
        rend=('Game/fight.html', context)

    ch.place=Place.objects.get(x=ch.x, y=ch.y, subloc_pk = ch.sublocation_pk)
    pack(user, 'ch', ch)
    return rend

def identification(item,ch):
    armor=Armor.objects.get(name=item)

    if armor.part == "helmet":
        ch.helmet=armor
    elif armor.part == "chestplate":
        ch.chestplate=armor
    elif armor.part == "leggings":
        ch.leggings=armor
    elif armor.part == "boots":
        ch.boots=armor

    buff = sum([x.protection for x in (ch.helmet, ch.chestplate, ch.leggings, ch.boots) if x])

    ch.max_hp=100 + buff + ch.allocated_points['hp'] * STATLEVEL_DEPENDENCIES['hp']
    ch.stat_check()

def equip_item(request, ch):
    item, section=request.POST['equipment'].split(',')

    if eval(f'{section}.objects.get(name = "{item}").level > ch.level'):
        return 'Я не знаю как владеть этим'

    if section=='Armor':
        identification(item,ch)

    elif section=='Weapon':
        weapon=Weapon.objects.get(name=item)
        ch.weapon=weapon
        ch.damage=10 + weapon.damage + ch.allocated_points['damage'] * STATLEVEL_DEPENDENCIES['damage']

    return f'Вы экипировали {item}'

def god_mode_stats(ch):
    ch.is_god = True
    ch.max_hp=10000
    ch.hp=ch.max_hp
    ch.damage=10000
    ch.coins=10000
    ch.exp = 10000
    check_level(ch)

def antigod_mode_stats(ch):
    ch.is_god = False
    ch.max_hp=100
    ch.damage=10
    ch.weapon=None
    ch.armor=None
    ch.coins=100
    ch.stat_check()