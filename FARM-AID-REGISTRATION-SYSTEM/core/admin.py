from django.contrib import admin
from django.utils.html import format_html
from .models import Farmer, AidApplication


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "id_number", "phone_number", "county")
    search_fields = ("full_name", "id_number", "phone_number", "county")


@admin.register(AidApplication)
class AidApplicationAdmin(admin.ModelAdmin):
    list_display = ("farmer", "resources_needed", "status", "colored_status", "applied_at")
    list_display_links = ("farmer",)  # ✅ makes farmer name clickable
    list_filter = ("status", "applied_at")
    list_editable = ("status",)  # ✅ now it's valid
    search_fields = ("farmer__full_name", "resources_needed", "status")

    def colored_status(self, obj):
        color = {
            "pending": "orange",
            "approved": "green",
            "rejected": "red",
        }.get(obj.status.lower(), "black")
        return format_html('<span style="color: {};">{}</span>', color, obj.status)

    colored_status.admin_order_field = "status"
    colored_status.short_description = "Status"
