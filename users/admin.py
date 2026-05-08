from django.contrib import admin
from .models import User, UserAddress, UserPhoneNumbers



class UserAdmin(admin.ModelAdmin):
    search_fields = (
        'full_name',
        'email',
        'cpf'
    )

    ordering = ('-date_joined',)

    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'username',
        'date_joined'
    )

    list_display_links = ('id',)

    list_filter = (
        'deleted',
        'is_staff',
        'is_superuser',
    )

    list_per_page = 20

admin.site.register(User, UserAdmin)


class UserAddressAdmin(admin.ModelAdmin):
    fields = (
        'user',
        'postal_code',
        'city',
        'district',
        'street_address',
        'number',
        'address_type',
        'complement',
        'is_primary'
    )
    autocomplete_fields = ['city']

    search_fields = (
        'user__full_name',
    )

    ordering = ('-created_at',)

    list_display = (
        'user',
        'street_address',
        'number',
        'is_primary',
        'created_at'
    )

    list_display_links = ('user',)

    list_filter = (
        'address_type',
        'deleted',
        'is_primary',
    )

    list_per_page = 20

admin.site.register(UserAddress, UserAddressAdmin)


class UserPhoneNumbersAdmin(admin.ModelAdmin):
    fields = (
        'user',
        'name',
        'phone_type',
        'country',
        'area_code',
        'phone_number',
        'is_primary',
    )

    search_fields = (
        'user__full_name',
    )

    ordering = ('-created_at',)

    list_display = (
        'user',
        'name',
        'phone_type',
        'country',
        'area_code',
        'phone_number',
        'is_primary',
        'created_at'
    )

    list_display_links = ('user',)

    list_filter = (
        'phone_type',
        'country',
        'deleted',
        'is_primary',
    )

    list_per_page = 20

admin.site.register(UserPhoneNumbers, UserPhoneNumbersAdmin)