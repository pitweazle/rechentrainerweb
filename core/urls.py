from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('uerbersicht/', views.uebersicht, name='uebersicht'),
    path('protokoll/', views.protokoll, name='protokoll'),
    path('protokoll/<int:zeile_id>', views.details, name='details'),
    path('<slug:slug>/', views.aufgabe, name='aufgabe'),
    path('optionen/<slug:slug>', views.optionen, name='optionen'),
    #path('wahl/<int:kategorie_id>', views.wahl, name='wahl'),
]
