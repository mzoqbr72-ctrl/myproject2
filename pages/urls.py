from django.urls import path
from . import views
from .views import RegistrationView, LoginView, ProfileView, ProfileEditView, ProjectCreateView

urlpatterns = [
    path('', views.home, name='home'),   
    path('game1/', views.game1, name='game1'),  
    path('game2/', views.game2, name='game2'), 
    path('game3/', views.game3, name='game3'),  
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('activate/<str:token>/', views.activate_account, name='activate'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/donate/', views.donate_to_project, name='donate_to_project'),
    path('projects/<int:project_id>/rate/', views.rate_project, name='rate_project'),
    path('projects/<int:project_id>/comment/', views.add_comment, name='add_comment'),
    path('projects/<int:project_id>/report/', views.report_project, name='report_project'),
    path('projects/<int:project_id>/cancel/', views.cancel_project, name='cancel_project'),
]
