from django.contrib import admin
from core.models import State, City, Country


class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_without_accents",
        "alpha_code",
        "country_code",
        "currency",
        "region",
        "sub_region"
    )

    search_fields = (
        "name", 
        "name_without_accents",
        "country_code",
        "alpha_code"
    )

    list_filter = (
        'region',
        'sub_region',
    )

admin.site.register(Country, CountryAdmin)


class StateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_without_accents",
        "country",
        "uf",
        "cod",
    )

    search_fields = (
        "name",
        "name_without_accents",
        "uf",
    )

admin.site.register(State, StateAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_without_accents",
        "state",
    )

    search_fields = (
        "name", "name_without_accents",
    )

admin.site.register(City, CityAdmin)