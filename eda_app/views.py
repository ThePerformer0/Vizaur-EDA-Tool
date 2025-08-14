from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .forms import DatasetUploadForm
from .models import Dataset
from django.http import JsonResponse
import os
import numpy as np
import pandas as pd


def convert_numpy_types(obj):
    """Convertit les types numpy/pandas en types Python natifs pour la sérialisation JSON"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def home(request):
    return render(request, 'eda_app/home.html')

def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            # Validation extension
            valid_extensions = ['.csv', '.xls', '.xlsx']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                messages.error(request, 'Format non supporté. Utilisez CSV, XLS ou XLSX.')
                return render(request, 'eda_app/upload.html', {'form': form})
            
            try:
                # Sauvegarde fichier
                file_path = default_storage.save(f'datasets/{file.name}', file)
                
                # Sauvegarde en base
                dataset = Dataset.objects.create(
                    name=file.name,
                    file_path=file_path,
                    size=file.size
                )
                
                # Analyse du fichier
                if dataset.analyze_and_update():
                    messages.success(request, f'Fichier {file.name} uploadé et analysé avec succès!')
                    return redirect('dataset_overview', dataset_id=dataset.id)
                else:
                    messages.error(request, 'Erreur lors de l\'analyse du fichier.')
                    
            except Exception as e:
                messages.error(request, f'Erreur lors du traitement: {str(e)}')
                
        return render(request, 'eda_app/upload.html', {'form': form})
    else:
        form = DatasetUploadForm()
    
    return render(request, 'eda_app/upload.html', {'form': form})

def dataset_list(request):
    datasets = Dataset.objects.all().order_by('-upload_date')
    return render(request, 'eda_app/dataset_list.html', {'datasets': datasets})


def dataset_overview(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    try:
        from .utils.data_analyzer import DatasetAnalyzer
        analyzer = DatasetAnalyzer(dataset.get_full_path())
        
        # Données de base
        basic_info = analyzer.get_basic_info()
        column_info = analyzer.detect_column_types()
        data_preview = analyzer.get_data_preview()
        
        # Données pour les statistiques
        numeric_columns = analyzer.get_numeric_columns()
        
        # Gestion des graphiques
        selected_column = request.GET.get('column')
        histogram_data = None
        column_stats = None
        
        if selected_column and selected_column in numeric_columns:
            histogram_data = analyzer.generate_histogram(selected_column)
            column_stats = analyzer.get_column_stats(selected_column)
        
        context = {
            'dataset': dataset,
            'basic_info': basic_info,
            'column_info': column_info,
            'data_preview': data_preview,
            'numeric_columns': numeric_columns,
            'selected_column': selected_column,
            'histogram_data': histogram_data,
            'column_stats': column_stats,
        }
        
        return render(request, 'eda_app/overview.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'analyse: {str(e)}')
        return redirect('dataset_list')


@csrf_exempt
def dataset_statistics(request, dataset_id):
    """Vue AJAX pour les statistiques descriptives"""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    try:
        from .utils.data_analyzer import DatasetAnalyzer
        analyzer = DatasetAnalyzer(dataset.get_full_path())
        
        # Statistiques descriptives pour toutes les colonnes numériques
        descriptive_stats = analyzer.get_descriptive_stats()
        
        # Informations sur les colonnes
        column_info = analyzer.detect_column_types()
        numeric_columns = analyzer.get_numeric_columns()
        
        # Statistiques par colonne sélectionnée
        selected_column = request.GET.get('column')
        column_stats = None
        if selected_column and selected_column in numeric_columns:
            column_stats = analyzer.get_column_stats(selected_column)
        
        data = {
            'descriptive_stats': convert_numpy_types(descriptive_stats.to_dict() if descriptive_stats is not None else None),
            'column_info': convert_numpy_types(column_info),
            'numeric_columns': convert_numpy_types(numeric_columns),
            'selected_column': selected_column,
            'column_stats': convert_numpy_types(column_stats),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        import traceback
        print(f"Erreur dans dataset_statistics: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def dataset_distributions(request, dataset_id):
    """Vue AJAX pour les distributions des variables"""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    try:
        from .utils.data_analyzer import DatasetAnalyzer
        analyzer = DatasetAnalyzer(dataset.get_full_path())
        
        # Informations sur les colonnes
        column_info = analyzer.detect_column_types()
        numeric_columns = analyzer.get_numeric_columns()
        categorical_columns = [col for col, info in column_info.items() if info['type'] == 'catégoriel']
        
        # Distributions pour les variables numériques
        numeric_distributions = {}
        for col in numeric_columns:
            try:
                histogram_data = analyzer.generate_histogram(col)
                column_stats = analyzer.get_column_stats(col)
                numeric_distributions[col] = {
                    'histogram': histogram_data,
                    'stats': convert_numpy_types(column_stats)
                }
            except Exception as e:
                print(f"Erreur pour la colonne numérique {col}: {e}")
                numeric_distributions[col] = {'error': str(e)}
        
        # Distributions pour les variables catégorielles
        categorical_distributions = {}
        for col in categorical_columns:
            try:
                bar_chart_data = analyzer.generate_bar_chart(col)
                categorical_distributions[col] = {
                    'bar_chart': bar_chart_data
                }
            except Exception as e:
                print(f"Erreur pour la colonne catégorielle {col}: {e}")
                categorical_distributions[col] = {'error': str(e)}
        
        data = {
            'numeric_distributions': numeric_distributions,
            'categorical_distributions': categorical_distributions,
            'column_info': convert_numpy_types(column_info),
            'numeric_columns': convert_numpy_types(numeric_columns),
            'categorical_columns': convert_numpy_types(categorical_columns),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        import traceback
        print(f"Erreur dans dataset_distributions: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def dataset_correlations(request, dataset_id):
    """Vue AJAX pour la matrice de corrélations"""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    try:
        from .utils.data_analyzer import DatasetAnalyzer
        analyzer = DatasetAnalyzer(dataset.get_full_path())
        
        # Matrice de corrélations
        correlation_matrix = analyzer.get_correlation_matrix()
        
        # Informations sur les colonnes numériques
        numeric_columns = analyzer.get_numeric_columns()
        
        # Corrélations par paires
        correlation_pairs = analyzer.get_correlation_pairs()
        
        data = {
            'correlation_matrix': convert_numpy_types(correlation_matrix.to_dict() if correlation_matrix is not None else None),
            'numeric_columns': convert_numpy_types(numeric_columns),
            'correlation_pairs': convert_numpy_types(correlation_pairs),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def delete_dataset(request, dataset_id):
    if request.method == 'POST':
        dataset = get_object_or_404(Dataset, id=dataset_id)
        
        try:
            # Supprimer le fichier physique
            if dataset.file_path and default_storage.exists(dataset.file_path):
                default_storage.delete(dataset.file_path)
            
            # Supprimer l'entrée en base
            dataset_name = dataset.name
            dataset.delete()
            
            messages.success(request, f'Dataset "{dataset_name}" supprimé avec succès.')
            
            # Retourner JSON si c'est une requête AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Dataset "{dataset_name}" supprimé avec succès.'})
            
            return redirect('dataset_list')
            
        except Exception as e:
            error_message = f'Erreur lors de la suppression: {str(e)}'
            messages.error(request, error_message)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_message})
            
            return redirect('dataset_list')
    
    # Si ce n'est pas POST, rediriger
    return redirect('dataset_list')
