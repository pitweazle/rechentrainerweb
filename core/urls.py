from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('modul/<int:modul_id>/', views.aufgabe, name='modul'),
    path('protokoll', views.protokoll, name='protokoll'),
]
