from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   
    path('game1/', views.game1, name='game1'),  
    path('game2/', views.game2, name='game2'), 
    path('game3/', views.game3, name='game3'),  
]
