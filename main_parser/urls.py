from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, serializers


urlpatterns = [
    path('userselectors/', views.SelectorsList.as_view()),
    path('selector/<int:pk>', views.SelectorsDetail.as_view()),

    path('account/', views.account, name='account'),
    path('account/add_selector/', views.add_selector, name='add_selector'),
    path('account/selectors/', views.user_selectors, name='user_selectors'),
    path('account/edit_selector/<str:slug>', views.edit_selector, name='edit_selector'),
    path('parse/', views.custom_parse, name='custom_parse'),
    path('parse/selectors/', views.custom_selectors, name='custom_selectors'),
    path('translate/', views.custom_translate, name='custom_translate'),
    path('result/', views.result, name='result'),

]

urlpatterns = format_suffix_patterns(urlpatterns)