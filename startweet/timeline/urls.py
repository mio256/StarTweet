from django.urls import path

from . import views

app_name = 'timeline'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.login, name='login'),
    path('oauth/', views.oauth, name='oauth'),
]