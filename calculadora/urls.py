from django.urls import path
from . import views

app_name = 'calculadora'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/salvar/', views.salvar_registro, name='salvar_registro'),
    path('api/excluir/<int:registro_id>/', views.excluir_registro, name='excluir_registro'),
]