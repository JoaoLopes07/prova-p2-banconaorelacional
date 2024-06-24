from django.shortcuts import render, get_object_or_404, redirect
from .models import Event
from django.contrib.auth.decorators import login_required
from events.forms import EventForm
from django.contrib.auth import login, authenticate
from .forms import CustomSignUpForm

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list') 
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

def event_update(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/event_update.html', {'form': form, 'event': event})

def event_delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

def signup(request):
    if request.method == 'POST':
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = CustomSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def my_view(request):
    return render(request, 'events/event_list.html', {'username': request.user.username})