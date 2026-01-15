
from django.db import models

class PageView(models.Model):
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('path', 'ip_address', 'date')

    def __str__(self):
        return f"{self.path} - {self.ip_address} - {self.date}"