from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='profile-update'),
    path('profile/settings/', views.UserProfileSettingsView.as_view(), name='profile-settings'),
    path('change-password/', views.change_password, name='change-password'),
    path('stats/', views.user_stats, name='user-stats'),
]

