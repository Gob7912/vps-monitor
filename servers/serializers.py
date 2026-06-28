from rest_framework import serializers
from .models import Server


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['id', 'name', 'ip_address', 'description', 'created_at', 'owner']
        read_only_fields = ['owner', 'created_at']