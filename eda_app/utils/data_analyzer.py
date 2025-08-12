import pandas as pd
import numpy as np
from datetime import datetime

class DatasetAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        try:
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(('.xls', '.xlsx')):
                self.df = pd.read_excel(self.file_path)
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du fichier: {str(e)}")
    
    def detect_column_types(self):
        column_info = {}
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            if dtype in ['int64', 'float64']:
                col_type = 'numérique'
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                col_type = 'date'
            elif self.df[col].nunique() / len(self.df) < 0.05 and len(self.df) > 20:
                col_type = 'catégoriel'
            else:
                col_type = 'texte'
            
            column_info[col] = {
                'type': col_type,
                'dtype': dtype,
                'missing_count': self.df[col].isnull().sum(),
                'missing_percent': round((self.df[col].isnull().sum() / len(self.df)) * 100, 2)
            }
        
        return column_info
    
    def get_basic_info(self):
        return {
            'num_rows': len(self.df),
            'num_columns': len(self.df.columns),
            'column_names': list(self.df.columns),
            'memory_usage': self.df.memory_usage(deep=True).sum()
        }
    
    def get_data_preview(self, head=5, tail=5):
        return {
            'head': self.df.head(head).to_html(classes='table table-striped', table_id='head-table'),
            'tail': self.df.tail(tail).to_html(classes='table table-striped', table_id='tail-table')
        }