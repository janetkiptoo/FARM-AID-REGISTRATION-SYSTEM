from django.contrib import admin
from django.utils.html import format_html
from .models import Farmer, AidApplication, ContactMessage, Notification
from .models import AidItem, SubAidItem

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "id_number", "phone_number", "county")
    search_fields = ("full_name", "id_number", "phone_number", "county")


@admin.register(AidApplication)
class AidApplicationAdmin(admin.ModelAdmin):
    list_display = ("farmer", "aid_item", "status", "colored_status", "applied_at")

    list_display_links = ("farmer",)
    list_filter = ("status", "applied_at")
    list_editable = ("status",)
    search_fields = ("farmer__full_name", "resources_needed", "status")

    
    def resources_needed(self, obj):
        return obj.aid_item.name  # or obj.aid_item.item_type etc.
    resources_needed.short_description = "Resources Needed"

    def colored_status(self, obj):
        color = {
            "pending": "orange",
            "approved": "green",
            "rejected": "red",
        }.get(obj.status.lower(), "black")
        return format_html('<span style="color: {};">{}</span>', color, obj.status)

    colored_status.admin_order_field = "status"
    colored_status.short_description = "Status"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)


admin.site.register(Notification)

class SubAidItemInline(admin.TabularInline):
    model = SubAidItem
    extra = 1  # how many empty sub-item slots to show by default



# ✅ Register AidItem with admin
@admin.register(AidItem)
class AidItemAdmin(admin.ModelAdmin):

    list_display = ('name', 'application_start', 'application_deadline', 'is_open_for_application')
    list_filter = ('name',)
    inlines = [SubAidItemInline]

    def get_subitems(self, obj):
        return ", ".join(obj.subitems)
    get_subitems.short_description = "Sub-Items"

    def colored_quantity(self, obj):
        """Show quantity in color depending on availability"""
        if obj.quantity_available <= 0:
            color = 'red'
        elif obj.quantity_available <= 5:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<b style="color:{};">{}</b>', color, obj.quantity_available)
    colored_quantity.short_description = "Quantity Available"

    def status_display(self, obj):
        """Show if aid is open or closed for application"""
        color = "green" if obj.is_open_for_application else "gray"
        text = "Open" if obj.is_open_for_application else "Closed"
        return format_html('<span style="color:{};">{}</span>', color, text)
    status_display.short_description = "Status"

    def stock_alert(self, obj):
        """Display a warning for low or no stock"""
        if obj.quantity_available <= 0:
            return format_html('<b style="color:red;">Out of Stock ⚠️</b>')
        elif obj.quantity_available <= 5:
            return format_html('<b style="color:orange;">Low Stock ⚠️</b>')
        return format_html('<span style="color:green;">OK ✅</span>')
    stock_alert.short_description = "Stock Alert"

