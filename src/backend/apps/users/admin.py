from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = ["avatar_preview", "username", "email", "first_name", "last_name", "formatted_phone", "twofa", "is_staff"]
    list_display_links = ["avatar_preview", "username"]
    
    readonly_fields = ["date_joined", "last_login", "avatar_preview"]
    
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("avatar", "twofa", "phone", "bio")}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {
            "classes": ("collapse",),
            "fields": ("first_name", "last_name", "email", "avatar", "twofa", "phone", "bio"),
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />', obj.avatar.url)
        return format_html('<div style="width: 32px; height: 32px; border-radius: 50%; background: #ccc;"></div>')
    
    avatar_preview.short_description = "Avatar"

    def formatted_phone(self, obj):
        if obj.phone:
            return obj.phone.as_international
        return "-"
    
    formatted_phone.short_description = "Phone Number"
