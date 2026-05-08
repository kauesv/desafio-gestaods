from django.contrib import admin
from .models import (
    DefaultPoints,
    CarPoints,
    DaysPoints,
    Nivel,
    Award,
    UserPoints,
    UserPointsHistory,
    ExportHistoricalPointsCSV
)


@admin.register(DefaultPoints)
class DefaultPointsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type_points", "points", "created_at")
    list_filter = ("type_points",)
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(CarPoints)
class CarPointsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category_car", "points", "activated", "created_at")
    list_filter = ("activated", "category_car")
    search_fields = ("name", "description")
    ordering = ("id",)


@admin.register(DaysPoints)
class DaysPointsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "start_date",
        "end_date",
        "points",
        "activated",
        "created_at",
    )
    list_filter = ("activated",)
    search_fields = ("name", "description")
    ordering = ("start_date",)


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "start_points",
        "end_points",
        "multiplier",
        "created_at",
    )
    search_fields = ("name", "description")
    ordering = ("start_points",)


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "points",
        "expiration_date",
        "activated",
        "created_at",
    )
    list_filter = ("activated",)
    search_fields = ("name", "description")
    ordering = ("expiration_date",)


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_points",
        "nivel",
        "points_to_next_tier",
        "lifetime_points_earned",
        "lifetime_points_redeemed",
        "created_at",
    )
    list_filter = ("nivel",)
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "nivel")
    ordering = ("-total_points",)


@admin.register(UserPointsHistory)
class UserPointsHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type_points",
        "points",
        "award",
        "created_at",
    )
    list_filter = ("type_points",)
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "award")
    ordering = ("-created_at",)


@admin.register(ExportHistoricalPointsCSV)
class ExportHistoricalPointsCSVAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file",
        "start_date",
        "end_date",
        "generated_successfully",
        "created_at",
    )

    list_filter = (
        "generated_successfully",
        "start_date",
        "end_date",
        "created_at",
    )

    search_fields = (
        "file",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-id",)

    fieldsets = (
        ("Informações do relatório", {
            "fields": (
                "file",
                "generated_successfully",
            )
        }),
        ("Período", {
            "fields": (
                "start_date",
                "end_date",
            )
        }),
        ("Metadados", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )