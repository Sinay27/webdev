# myproject/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('newsapi.urls')),  # This line includes the URLs from your 'newsapi' app
]
