from django.urls import path
from .views import register, login, logout, profile

urlpatterns = [
    path("register/", register, name='user-register'),
    path("login/", login, name='user-login'),
    path("logout/", logout, name='user-logout'),
    path("profile/", profile, name='user-profile'),
]