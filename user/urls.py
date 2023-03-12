from django.urls import path
from django.urls.conf import include
from .views import register
app_name='user'
urlpatterns=[
    path('', include('django.contrib.auth.urls')),
    path('register/', register, name='registration')
]