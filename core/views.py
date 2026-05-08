from django.http import JsonResponse
from core.serializers import StateSerializer, CitySerializer
from core.models import State, City
from rest_framework import viewsets, generics, filters
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend


def index(request):
    return JsonResponse({'api_version': '1.0', "api_name": "Aluguel de Carros LTDA"}) 


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    http_method_names = ['get',]
    ordering_fields = ['created_at']


class CityViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    http_method_names = ['get',]
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['state']
    search_fields = ['state', 'name']