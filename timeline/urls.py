from django.urls import path

from . import views, tweepy_func

app_name = 'timeline'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('user/<int:id>/', views.UserView.as_view(), name='user'),
    path('list/<int:id>/', views.ListView.as_view(), name='list'),
    path('login/', tweepy_func.login, name='login'),
    path('oauth/', tweepy_func.oauth, name='oauth'),
    path('like_home/', tweepy_func.like_home, name='like_home'),
]