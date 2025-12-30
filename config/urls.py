from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add API includes here when ready, e.g.
    # path('api/v1/users/', include('apps.users.urls')),
]

