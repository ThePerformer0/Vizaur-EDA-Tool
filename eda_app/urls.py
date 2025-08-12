from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('dataset/<int:dataset_id>/', views.dataset_overview, name='dataset_overview'),
]