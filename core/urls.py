from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('modul/<int:modul_id>/', views.aufgabe, name='aufgabe'),
    path('protokoll/', views.protokoll, name='protokoll'),
    path('protokoll/<int:zeile_id>', views.details, name='details'),
    path('auswahl/', views.auswahl, name='auswahl'),

    #path('auswahl/<int:kategorie_id>', views.auswahl, name='auswahl'),
    #path('auswahl/<int:kategorie_id>/wahl/', views.wahl, name='wahl'),
]
