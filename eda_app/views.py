from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from .forms import DatasetUploadForm
from .models import Dataset
import os


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
        
        context = {
            'dataset': dataset,
            'basic_info': analyzer.get_basic_info(),
            'column_info': analyzer.detect_column_types(),
            'data_preview': analyzer.get_data_preview(),
        }
        
        return render(request, 'eda_app/overview.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'analyse: {str(e)}')
        return redirect('dataset_list')