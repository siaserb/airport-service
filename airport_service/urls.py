from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from airport_service import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/airport/", include("airport.urls", namespace="airport")),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
