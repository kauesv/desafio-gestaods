from rest_framework import serializers
from .models import State
from .models import City
from .models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):

    state = StateSerializer(many=False)

    class Meta:
        model = City
        fields = '__all__'
