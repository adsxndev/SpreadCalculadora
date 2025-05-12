from django.db import models
from django.utils import timezone
from decimal import Decimal

class SpreadRegistro(models.Model):
    data_registro = models.DateTimeField(default=timezone.now)
    spot_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    short_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    spread_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    spot_fechamento = models.DecimalField(max_digits=10, decimal_places=2)
    short_fechamento = models.DecimalField(max_digits=10, decimal_places=2)
    spread_fechamento = models.DecimalField(max_digits=10, decimal_places=2)
    lucro = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Operação {self.id} - {self.data_registro.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # Calcular spread de abertura se não estiver definido (normal)
        if not self.spread_abertura:
            self.spread_abertura = ((self.short_abertura - self.spot_abertura) / self.spot_abertura) * Decimal('100.0')
        
        # Calcular spread de fechamento se não estiver definido (invertido)
        if not self.spread_fechamento:
            self.spread_fechamento = -((self.short_fechamento - self.spot_fechamento) / self.spot_fechamento) * Decimal('100.0')
        
        # Calcular lucro se não estiver definido
        if not self.lucro:
            self.lucro = self.spread_abertura + self.spread_fechamento
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Registro de Spread"
        verbose_name_plural = "Registros de Spread"
        ordering = ['-data_registro']