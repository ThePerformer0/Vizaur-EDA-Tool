from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('dataset/<int:dataset_id>/', views.dataset_overview, name='dataset_overview'),
    path('dataset/<int:dataset_id>/delete/', views.delete_dataset, name='delete_dataset'),
    
    # URLs pour les vues AJAX des onglets
    path('dataset/<int:dataset_id>/statistics/', views.dataset_statistics, name='dataset_statistics'),
    path('dataset/<int:dataset_id>/distributions/', views.dataset_distributions, name='dataset_distributions'),
    path('dataset/<int:dataset_id>/correlations/', views.dataset_correlations, name='dataset_correlations'),
]