from django.shortcuts import render, redirect
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
            
            # Sauvegarde fichier
            file_path = default_storage.save(f'datasets/{file.name}', file)
            
            # Sauvegarde en base
            dataset = Dataset.objects.create(
                name=file.name,
                file_path=file_path,
                size=file.size
            )
            
            messages.success(request, f'Fichier {file.name} uploadé avec succès!')
            return redirect('dataset_list')
    else:
        form = DatasetUploadForm()
    
    return render(request, 'eda_app/upload.html', {'form': form})

def dataset_list(request):
    datasets = Dataset.objects.all().order_by('-upload_date')
    return render(request, 'eda_app/dataset_list.html', {'datasets': datasets})