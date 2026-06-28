from rest_framework import serializers
from .models import Metric, Alert


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = ['id', 'server', 'cpu_usage', 'ram_usage', 'disk_usage', 'created_at']
        read_only_fields = ['created_at']

    def validate_cpu_usage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("CPU usage 0 va 100 oralig'ida bo'lishi kerak")
        return value

    def validate_ram_usage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("RAM usage 0 va 100 oralig'ida bo'lishi kerak")
        return value

    def validate_disk_usage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Disk usage 0 va 100 oralig'ida bo'lishi kerak")
        return value


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'server', 'message', 'level', 'created_at']
        read_only_fields = ['created_at']