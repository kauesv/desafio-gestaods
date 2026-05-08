from django.contrib import admin
from .models import Car, Rental


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'category', 'daily_rate', 'available']
    list_filter = ['available', 'brand']
    search_fields = ['brand', 'model']


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'user', 'start_date', 'end_date', 'returned']
    list_filter = ['returned', 'start_date']
    search_fields = ['user__full_name', 'user__email']
    date_hierarchy = 'start_date'

