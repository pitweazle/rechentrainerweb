from django.urls import path

from .import views

urlpatterns=[
    path("forum/", views.forum),
    path("eingabe", views.eingabe)]