from django.contrib import admin
from django.urls import path, include

from .health import health

urlpatterns = [
    path('admin/', admin.site.urls),

    # App APIs (versioned) - migrated from Backend/urls.py
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/restaurants/', include('apps.restaurants.urls')),
    path('api/v1/tables/', include('apps.tables.urls')),
    path('api/v1/sessions/', include('apps.sessions.urls')),
    path('api/v1/menu/', include('apps.menu.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/staff/', include('apps.staff.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),


    # alias for backwards-compat / convenience
    path('api/health', health),
]
