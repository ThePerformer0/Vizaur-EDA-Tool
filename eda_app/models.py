from django.db import models
from django.utils import timezone

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    size = models.IntegerField()  # en bytes
    upload_date = models.DateTimeField(default=timezone.now)
    num_rows = models.IntegerField(null=True, blank=True)
    num_columns = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, default='uploaded')
    
    def __str__(self):
        return self.name