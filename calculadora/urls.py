from django.urls import path
from . import views

app_name = 'calculadora'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('api/salvar/', views.salvar_registro, name='salvar_registro'),
    path('api/excluir/<int:registro_id>/', views.excluir_registro, name='excluir_registro'),
]
