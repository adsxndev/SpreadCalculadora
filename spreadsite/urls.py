from django.contrib import admin
from django.urls import path, include
from calculadora import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculadora.urls')),  # Inclui as URLs do app 'calculadora'
]
