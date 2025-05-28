from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

class SpreadRegistro(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_registro = models.DateTimeField(default=timezone.now)
    spot_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    short_abertura = models.DecimalField(max_digits=10, decimal_places=2)
    spread_abertura = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    spot_fechamento = models.DecimalField(max_digits=10, decimal_places=2)
    short_fechamento = models.DecimalField(max_digits=10, decimal_places=2)
    spread_fechamento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lucro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Operação {self.id} - {self.data_registro.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        if self.spread_abertura is None:
            self.spread_abertura = ((self.short_abertura - self.spot_abertura) / self.spot_abertura) * Decimal('100.0')

        if self.spread_fechamento is None:
            self.spread_fechamento = -((self.short_fechamento - self.spot_fechamento) / self.spot_fechamento) * Decimal('100.0')

        if self.lucro is None:
            self.lucro = self.spread_abertura + self.spread_fechamento

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Registro de Spread"
        verbose_name_plural = "Registros de Spread"
        ordering = ['-data_registro']
