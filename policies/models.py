from django.db import models
from django.conf import settings

class Policy(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    description = models.TextField()
    name = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Policy created by {self.created_by.username} on {self.created_date.strftime('%Y-%m-%d')}"
