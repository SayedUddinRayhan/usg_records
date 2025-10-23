from django.urls import path
from . import views

app_name = 'masterdata'

urlpatterns = [
    # exam names
    path('exam-names/', views.examname_list, name='examname_list'),
    path('exam-names/add/', views.examname_create, name='examname_create'),
    path('exam-names/<int:pk>/edit/', views.examname_edit, name='examname_edit'),
    path('exam-names/<int:pk>/delete/', views.examname_delete, name='examname_delete'),

    # exam types
    path('exam-types/', views.examtype_list, name='examtype_list'),
    path('exam-types/add/', views.examtype_create, name='examtype_create'),
    path('exam-types/<int:pk>/edit/', views.examtype_edit, name='examtype_edit'),
    path('exam-types/<int:pk>/delete/', views.examtype_delete, name='examtype_delete'),

    # referrers
    path('referrers/', views.referrer_list, name='referrer_list'),
    path('referrers/add/', views.referrer_create, name='referrer_create'),
    path('referrers/<int:pk>/edit/', views.referrer_edit, name='referrer_edit'),
    path('referrers/<int:pk>/delete/', views.referrer_delete, name='referrer_delete'),

    # sonologists
    path('sonologists/', views.sonologist_list, name='sonologist_list'),
    path('sonologists/add/', views.sonologist_create, name='sonologist_create'),
    path('sonologists/<int:pk>/edit/', views.sonologist_edit, name='sonologist_edit'),
    path('sonologists/<int:pk>/delete/', views.sonologist_delete, name='sonologist_delete'),
]
