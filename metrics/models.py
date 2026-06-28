from django.db import models
from servers.models import Server


class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='metrics')
    cpu_usage = models.FloatField()
    ram_usage = models.FloatField()
    disk_usage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name} - {self.created_at}"


class Alert(models.Model):
    LEVEL_CHOICES = [
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='alerts')
    message = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='warning')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.level.upper()}: {self.message}"