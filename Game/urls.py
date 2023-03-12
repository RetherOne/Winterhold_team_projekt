from django.urls import path
from .views import antigod_mode, gode_mode, greet, new_game, shop, start_page, stat_update,travel,fight, new_game_page, \
    rest, equip, eat, new_game, travel_page, finish_game, show_hint
app_name='Game'
urlpatterns=[
    path('', start_page, name='start_page'),
    path('greet/', greet, name='greetings'),
    path('travel/', travel, name='travel'),
    path('travel_page/', travel_page, name='travel_page'),
    path('fight/', fight, name='fight'),
    path('shop/<str:place>/', shop, name='shop'),
    path('rest/', rest, name='rest'),
    path('equip/', equip, name='equip'),
    path('stat_update/', stat_update, name='stat_update'),
    path('eat/', eat, name='eat'),
    path('show_hint/', show_hint, name='show_hint'),
    path('finish/', finish_game, name='finish_game'),
    path('new_game_page/', new_game_page, name='new_game_page'),
    path('new_game/', new_game, name='new_game'),
    path('god_mode/', gode_mode, name='god_mode'),
    path('antigod_mode/', antigod_mode, name='antigod_mode'),
]