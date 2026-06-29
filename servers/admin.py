from django.contrib import admin
from .models import Server

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'ip_address']
