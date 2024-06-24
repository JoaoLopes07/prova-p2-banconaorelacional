from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('new/', views.event_create, name='event_create'),
    path('update/<int:event_id>/', views.event_update, name='event_update'),
    path('delete/<int:event_id>/', views.event_delete, name='event_delete'),
    path('protected/', login_required(views.my_view), name='my_view'),
    path('signup/', views.signup, name='signup'),
    path('', lambda request: redirect('http://127.0.0.1:8001/', permanent=False)),
]
