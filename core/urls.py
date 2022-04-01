from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
<<<<<<< HEAD

    path('protokoll/', views.protokoll, name='protokoll'),
    path('protokoll/<int:zeile_id>', views.details, name='details'),
    #path('modul/<slug:slug>', views.modul, name='modul'),   
    path('<slug:slug>/', views.aufgabe, name='aufgabe'),
    path('auswahl/<int:kategorie_id>', views.auswahl, name='auswahl'),
    path('wahl/<int:kategorie_id>', views.wahl, name='wahl'),
=======
    path('modul/<int:modul_id>/', views.aufgabe, name='aufgabe'),
    path('protokoll/', views.protokoll, name='protokoll'),
    path('protokoll/<int:zeile_id>', views.details, name='details'),
    path('auswahl/', views.auswahl, name='auswahl'),

    #path('auswahl/<int:kategorie_id>', views.auswahl, name='auswahl'),
    #path('auswahl/<int:kategorie_id>/wahl/', views.wahl, name='wahl'),
>>>>>>> 077ad612518978bb87d7db2e0d84a1163ef49987
]
