from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/airport/", include("airport.urls", namespace="airport")),
    path("__debug__/", include("debug_toolbar.urls")),
]
