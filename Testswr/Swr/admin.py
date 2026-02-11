from django.contrib import admin

# Register your models here.
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "mobile",
        "role",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "mobile",
    )

    list_filter = (
        "role",
        "created_at",
    )

    ordering = ("-created_at",)

    list_per_page = 25

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("first_name", "last_name", "email", "mobile", "role")
        }),
        ("Metadata", {
            "fields": ("created_at",),
        }),
    )