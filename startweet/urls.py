from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('timeline/', include('timeline.urls')),
    path('admin/', admin.site.urls),
]
