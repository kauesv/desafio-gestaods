from rest_framework import serializers
from .models import Car, Rental


class CarSerializer(serializers.ModelSerializer):
    """Serializer para modelo Carro"""
    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'year', 'category', 'daily_rate', 'available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = [
            'id', 'car', 'user',
            'start_date', 'end_date', 'total_cost', 'returned',
            'actual_return_date', 'late_fee', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RentalCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField()
    days = serializers.IntegerField(min_value=1)

