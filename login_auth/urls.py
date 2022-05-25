from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.urlpatterns import format_suffix_patterns

from login_auth import views


urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('', views.main, name='main'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register_user, name='register_user'),
    path('password_reset/', views.password_reset, name='password_reset'),

]

urlpatterns = format_suffix_patterns(urlpatterns)