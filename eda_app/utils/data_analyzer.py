import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import chardet



class DatasetAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        try:
            if self.file_path.endswith('.csv'):                
                # Lire un échantillon du fichier pour détecter l'encodage
                with open(self.file_path, 'rb') as f:
                    raw_data = f.read(10000)  # Lire les premiers 10KB
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] if detected['confidence'] > 0.7 else 'utf-8'
                
                try:
                    self.df = pd.read_csv(self.file_path, encoding=encoding)
                    print(f"Fichier chargé avec l'encodage détecté: {encoding}")
                except:
                    # Fallback avec les encodages courants
                    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'cp1252']
                    for enc in encodings:
                        try:
                            self.df = pd.read_csv(self.file_path, encoding=enc)
                            print(f"Fichier chargé avec l'encodage de secours: {enc}")
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        self.df = pd.read_csv(self.file_path, encoding='utf-8', errors='replace')
                        
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

    def get_numeric_columns(self):
        """Retourne la liste des colonnes numériques"""
        return self.df.select_dtypes(include=[np.number]).columns.tolist()

    def get_descriptive_stats(self):
        """Calcule les statistiques descriptives pour toutes les colonnes numériques"""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return None
        
        try:
            stats = numeric_df.describe()
            
            # Ajouter quelques stats supplémentaires avec gestion d'erreur
            try:
                stats.loc['variance'] = numeric_df.var()
            except:
                stats.loc['variance'] = pd.Series([None] * len(numeric_df.columns), index=numeric_df.columns)
            
            try:
                stats.loc['skewness'] = numeric_df.skew()
            except:
                stats.loc['skewness'] = pd.Series([None] * len(numeric_df.columns), index=numeric_df.columns)
            
            try:
                stats.loc['kurtosis'] = numeric_df.kurtosis()
            except:
                stats.loc['kurtosis'] = pd.Series([None] * len(numeric_df.columns), index=numeric_df.columns)
            
            return stats.round(3)
        except Exception as e:
            print(f"Erreur dans get_descriptive_stats: {e}")
            return None

    def get_column_stats(self, column_name):
        """Statistiques détaillées pour une colonne spécifique"""
        if column_name not in self.df.columns:
            return None
        
        col_data = self.df[column_name]
        if not pd.api.types.is_numeric_dtype(col_data):
            return None
        
        # Supprimer les valeurs manquantes pour les calculs
        clean_data = col_data.dropna()
        
        if len(clean_data) == 0:
            return None
        
        try:
            stats = {
                'count': len(clean_data),
                'missing': col_data.isnull().sum(),
                'mean': clean_data.mean(),
                'median': clean_data.median(),
                'mode': clean_data.mode().iloc[0] if not clean_data.mode().empty else None,
                'std': clean_data.std(),
                'variance': clean_data.var(),
                'min': clean_data.min(),
                'max': clean_data.max(),
                'q1': clean_data.quantile(0.25),
                'q3': clean_data.quantile(0.75),
                'iqr': clean_data.quantile(0.75) - clean_data.quantile(0.25),
                'range': clean_data.max() - clean_data.min()
            }
            
            # Ajouter skewness et kurtosis avec gestion d'erreur
            try:
                stats['skewness'] = clean_data.skew()
            except:
                stats['skewness'] = None
                
            try:
                stats['kurtosis'] = clean_data.kurtosis()
            except:
                stats['kurtosis'] = None
            
            return {k: round(v, 3) if isinstance(v, (int, float)) and v is not None else v for k, v in stats.items()}
            
        except Exception as e:
            print(f"Erreur dans get_column_stats pour {column_name}: {e}")
            return None

    def generate_histogram(self, column_name, bins=30):
        """Génère un histogramme pour une colonne numérique"""
        if column_name not in self.df.columns:
            return None
        
        col_data = self.df[column_name].dropna()
        if not pd.api.types.is_numeric_dtype(col_data) or len(col_data) == 0:
            return None
        
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histogramme avec seaborn pour un meilleur style
        sns.histplot(data=col_data, bins=bins, kde=True, ax=ax, alpha=0.7)
        
        ax.set_title(f'Distribution de {column_name}', fontsize=14, fontweight='bold')
        ax.set_xlabel(column_name, fontsize=12)
        ax.set_ylabel('Fréquence', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return image_base64

    def generate_bar_chart(self, column_name, max_categories=20):
        """Génère un graphique en barres pour une colonne catégorielle"""
        if column_name not in self.df.columns:
            return None
        
        col_data = self.df[column_name].dropna()
        if len(col_data) == 0:
            return None
        
        # Compter les occurrences
        value_counts = col_data.value_counts()
        
        # Limiter le nombre de catégories pour la lisibilité
        if len(value_counts) > max_categories:
            top_values = value_counts.head(max_categories - 1)
            other_count = value_counts.iloc[max_categories - 1:].sum()
            value_counts = pd.concat([top_values, pd.Series({'Autres': other_count})])
        
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Graphique en barres
        bars = ax.bar(range(len(value_counts)), value_counts.values, alpha=0.7, color='skyblue')
        
        # Personnalisation
        ax.set_title(f'Distribution de {column_name}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Catégories', fontsize=12)
        ax.set_ylabel('Fréquence', fontsize=12)
        ax.set_xticks(range(len(value_counts)))
        ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Ajouter les valeurs sur les barres
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return image_base64

    def get_correlation_matrix(self):
        """Calcule la matrice de corrélations pour les colonnes numériques"""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty or numeric_df.shape[1] < 2:
            return None
        
        # Calculer la matrice de corrélations
        corr_matrix = numeric_df.corr()
        
        return corr_matrix.round(3)

    def get_correlation_pairs(self, threshold=0.5):
        """Retourne les paires de variables avec une corrélation significative"""
        corr_matrix = self.get_correlation_matrix()
        if corr_matrix is None:
            return []
        
        # Créer une liste de paires avec leurs corrélations
        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) >= threshold:
                    pairs.append({
                        'variable1': col1,
                        'variable2': col2,
                        'correlation': corr_value,
                        'strength': 'forte' if abs(corr_value) >= 0.7 else 'modérée' if abs(corr_value) >= 0.5 else 'faible',
                        'direction': 'positive' if corr_value > 0 else 'négative'
                    })
        
        # Trier par valeur absolue de corrélation décroissante
        pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return pairs

    def generate_correlation_heatmap(self):
        """Génère une heatmap des corrélations"""
        corr_matrix = self.get_correlation_matrix()
        if corr_matrix is None:
            return None
        
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Heatmap avec seaborn
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8}, ax=ax)
        
        ax.set_title('Matrice de Corrélations', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Convertir en base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return image_base64