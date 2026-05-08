from django.urls import path, include
from rest_framework import routers
from rentals import views

app_name = 'rentals'

router = routers.DefaultRouter()

urlpatterns = [
    path('', views.index, name='index'),
    path('cars', views.get_cars, name='get_cars'),
    path('cars/<int:car_id>', views.get_car, name='get_car'),
    path('list', views.get_rentals, name='get_rentals'),
    path('create', views.create_rental, name='create_rental'),
    path('<int:rental_id>/return', views.return_rental, name='return_rental'),
    path('customer/<str:customer_email>', views.get_customer_rentals, name='get_customer_rentals'),
    path('stats', views.get_stats, name='get_stats'),
]