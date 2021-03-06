from django.urls import path

from . import views

urlpatterns = [
    path('', views.kategorien, name='kategorien'),
    path('uerbersicht/', views.uebersicht, name='uebersicht'),
    path('protokoll/', views.protokoll, name='protokoll'),
    path('protokoll/<int:zeile_id>', views.details, name='details'),
    path('abbrechen/<int:zaehler_id>', views.abbrechen, name='abbrechen'),
    path('loesung/<int:zaehler_id>/', views.loesung, name='loesung'),
    path('hilfe/<int:zaehler_id>/<int:protokoll_id>/', views.hilfe, name='hilfe'),
    path('<slug:slug>/', views.main, name='main'),
    path('optionen/<slug:slug>', views.optionen, name='optionen'),
]
