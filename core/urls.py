from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('protokoll/', views.protokoll, name='protokoll'),
    path('protokoll/<int:zeile_id>', views.details, name='details'),
    #path('modul/<slug:slug>', views.modul, name='modul'),   
    path('<slug:slug>/', views.aufgabe, name='aufgabe'),
    path('auswahl/<int:kategorie_id>', views.auswahl, name='auswahl'),
    path('wahl/<int:kategorie_id>', views.wahl, name='wahl'),
]
