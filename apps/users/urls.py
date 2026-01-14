from django.urls import path
from .views import (
    register,
    login,
    logout,
    refresh_token,
    profile,
    update_profile,
    change_password,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', register, name='user-register'),
    path('login/', login, name='user-login'),
    path('logout/', logout, name='user-logout'),
    path('refresh/', refresh_token, name='user-refresh-token'),

    # User profile endpoints
    path('profile/', profile, name='user-profile'),
    path('profile/update/', update_profile, name='user-profile-update'),
    path('profile/change-password/', change_password, name='user-change-password'),
]