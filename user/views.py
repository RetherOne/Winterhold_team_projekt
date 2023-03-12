from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from Game.game_classes import Character, pack
# Create your views here.
def register(request):
    if request.method!='POST':
        form=UserCreationForm()
    else:
        form=UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user=form.save()
            login(request, new_user)
            pack(str(new_user.pk), 'ch', Character())
            return redirect('Game:greetings')

    context={'form':form}
    return render(request, 'User/registration.html', context)

    