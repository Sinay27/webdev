# newsapi/urls.py

from django.urls import path
from . import views  

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('stories/', views.stories, name='stories'),
    path('stories/<int:story_id>/', views.delete_story, name='delete_story'),
    # Add other paths as needed
]
