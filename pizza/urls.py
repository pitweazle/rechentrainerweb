from django.urls import path
from pizza import views

urlpatterns=[
    path('pizza', views.pizza, name='pizza'),
    path('order', views.order, name='order'),
    path('pizzas', views.pizzas, name='pizzas'),
]