from django.db import models
from django.utils import timezone
import os
from django.conf import settings

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    size = models.IntegerField()
    upload_date = models.DateTimeField(default=timezone.now)
    num_rows = models.IntegerField(null=True, blank=True)
    num_columns = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, default='uploaded')
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.file_path)
    
    def analyze_and_update(self):
        try:
            from .utils.data_analyzer import DatasetAnalyzer
            analyzer = DatasetAnalyzer(self.get_full_path())
            basic_info = analyzer.get_basic_info()
            
            self.num_rows = basic_info['num_rows']
            self.num_columns = basic_info['num_columns']
            self.status = 'analyzed'
            self.save()
            
            return True
        except Exception as e:
            self.status = 'error'
            self.save()
            return False