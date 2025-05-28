from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from decimal import Decimal
import json

from .models import SpreadRegistro

# Tela principal protegida por login
@login_required(login_url='/login/')
def index(request):
    registros = SpreadRegistro.objects.filter(user=request.user).order_by('-data_registro')
    return render(request, 'calculadora/index.html', {'registros': registros})

# View de login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('calculadora:index')  # Redireciona para index da app calculadora
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'calculadora/login.html')

# View de cadastro
def cadastro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validações básicas
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'calculadora/cadastro.html')

        if password1 != password2:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'calculadora/cadastro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe.')
            return render(request, 'calculadora/cadastro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email já está em uso.')
            return render(request, 'calculadora/cadastro.html')

        # Criar o usuário
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        messages.success(request, 'Cadastro realizado com sucesso! Você já pode fazer login.')
        return redirect('calculadora:login')

    return render(request, 'calculadora/cadastro.html')

# Salvar registro (API) protegida por login
@csrf_exempt
@login_required(login_url='/login/')
def salvar_registro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            required_fields = ['spot_abertura', 'short_abertura', 'spot_fechamento', 'short_fechamento']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'Campo {field} é obrigatório'}, status=400)

            spot_abertura = Decimal(data['spot_abertura'])
            short_abertura = Decimal(data['short_abertura'])
            spot_fechamento = Decimal(data['spot_fechamento'])
            short_fechamento = Decimal(data['short_fechamento'])

            spread_abertura = ((short_abertura - spot_abertura) / spot_abertura) * Decimal('100.0')
            spread_fechamento = -((short_fechamento - spot_fechamento) / spot_fechamento) * Decimal('100.0')
            lucro = spread_abertura + spread_fechamento

            registro = SpreadRegistro(
                 user=request.user,
                spot_abertura=spot_abertura,
                short_abertura=short_abertura,
                spread_abertura=spread_abertura,
                spot_fechamento=spot_fechamento,
                short_fechamento=short_fechamento,
                spread_fechamento=spread_fechamento,
                lucro=lucro
            )
            registro.save()

            return JsonResponse({
                'success': True,
                'registro': {
                    'id': registro.id,
                    'data': registro.data_registro.strftime('%d/%m/%Y'),
                    'spot_abertura': float(registro.spot_abertura),
                    'short_abertura': float(registro.short_abertura),
                    'spread_abertura': float(registro.spread_abertura),
                    'spot_fechamento': float(registro.spot_fechamento),
                    'short_fechamento': float(registro.short_fechamento),
                    'spread_fechamento': float(registro.spread_fechamento),
                    'lucro': float(registro.lucro)
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)

# Excluir registro (API) protegida por login
@csrf_exempt
@login_required(login_url='/login/')
def excluir_registro(request, registro_id):
    if request.method == 'DELETE':
        try:
            registro = SpreadRegistro.objects.get(id=registro_id, user=request.user)
            registro.delete()
            return JsonResponse({'success': True})
        except SpreadRegistro.DoesNotExist:
            return JsonResponse({'error': 'Registro não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)
