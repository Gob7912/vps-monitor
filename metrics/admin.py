from django.contrib import admin
from .models import Metric, Alert

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['server', 'cpu_usage', 'ram_usage', 'disk_usage', 'created_at']
    list_filter = ['created_at']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['server', 'level', 'message', 'created_at']
    list_filter = ['level', 'created_at']
