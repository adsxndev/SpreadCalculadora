from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SpreadRegistro
import json
from decimal import Decimal

def index(request):
    # Alterado para usar data_registro em vez de data
    registros = SpreadRegistro.objects.all().order_by('-data_registro')
    return render(request, 'calculadora/index.html', {'registros': registros})

@csrf_exempt
def salvar_registro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar dados
            required_fields = ['spot_abertura', 'short_abertura', 'spot_fechamento', 'short_fechamento']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'Campo {field} é obrigatório'}, status=400)
            
            # Calcular spreads
            spot_abertura = Decimal(data['spot_abertura'])
            short_abertura = Decimal(data['short_abertura'])
            spot_fechamento = Decimal(data['spot_fechamento'])
            short_fechamento = Decimal(data['short_fechamento'])
            
            # Spread de abertura (normal)
            spread_abertura = ((short_abertura - spot_abertura) / spot_abertura) * Decimal('100.0')
            
            # Spread de fechamento (invertido)
            spread_fechamento = -((short_fechamento - spot_fechamento) / spot_fechamento) * Decimal('100.0')
            
            # Lucro
            lucro = spread_abertura + spread_fechamento
            
            # Criar novo registro
            registro = SpreadRegistro(
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
@csrf_exempt
def excluir_registro(request, registro_id):
    if request.method == 'DELETE':
        try:
            registro = SpreadRegistro.objects.get(id=registro_id)
            registro.delete()
            return JsonResponse({'success': True})
        except SpreadRegistro.DoesNotExist:
            return JsonResponse({'error': 'Registro não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)