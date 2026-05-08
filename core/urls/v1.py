from django.urls import path, include
from rest_framework import routers
from core import views

app_name = 'core'

router = routers.DefaultRouter()

router.register(r'states', views.StateViewSet, basename='states')
router.register(r'cities', views.CityViewSet, basename='cities')

urlpatterns = [
    path('', include(router.urls)),
]
