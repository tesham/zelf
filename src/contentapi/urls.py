from django.contrib import admin
from django.urls import path

from src.contents.views import ContentAPIView, ContentStatsAPIView, ContentAPIViewUpdate, ContentStatsAPIViewUpdated

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/contents/stats/", ContentStatsAPIViewUpdated.as_view(), name="api-contents-stats"),
    path("api/contents/", ContentAPIViewUpdate.as_view(), name="api-contents"),
]
