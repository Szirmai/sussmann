from django.db import models

# Create your models here.

class CostType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Cost(models.Model):
    title = models.CharField(max_length=200, null=True)
    cost = models.IntegerField(null=True)
    cause = models.CharField(max_length=400, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey(CostType, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title
    

