from django.urls import path

from . import views

app_name = 'timeline'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('user/<int:id>/', views.UserView.as_view(), name='user'),
    path('login/', views.login, name='login'),
    path('oauth/', views.oauth, name='oauth'),
]