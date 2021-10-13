from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import DateField
from django.db.models.fields.related import ManyToManyField
from django.utils import timezone


class SU(models.Model):
    Nome_SU = models.CharField(max_length=20)

    def __str__(self):
        return self.Nome_SU

class  PostGrad(models.Model):
    Nome_PG = models.CharField(max_length=10)

    def __str__(self):
        return self.Nome_PG

class Militar(models.Model):
    NomeG_Mil = models.CharField(null=False, blank=False, max_length=20)
    Nome_Mil = models.CharField(null=False, blank=False, max_length=100)
    DtNsc_Mil = models.DateField(null=False, blank=False)
    DtPrac_Mil  = models.DateField(null=False, blank=False)
    DtProm_Mil = models.DateField(null=False, blank=False)
    Vsb_Mil = models.BooleanField(null=True)

    Id_SU = models.ForeignKey(SU, null=False, blank=False, on_delete=models.CASCADE)
    Id_PG = models.ForeignKey(PostGrad, null=False, blank=False, on_delete=models.CASCADE)

class TipoEscala(models.Model):
    Nome_TipEsc = models.CharField(max_length=50)
    "Id_Mil = models.ManyToManyField(Militar)"

class SubTipoEscala(models.Model):
    Nome_SubTipEsc = models.CharField(max_length=50)
    Prioridade_SubTipEsc = models.IntegerField
    Id_TipEsc = models.ForeignKey(TipoEscala, on_delete=models.CASCADE)

class Militar_Tipo(models.Model):
    Id_Mil = models.ForeignKey(Militar, on_delete=models.CASCADE)
    Id_TipEsc = models.ForeignKey(TipoEscala, on_delete=models.CASCADE)
    DtSv_P_Mil_TipEsc = models.DateField
    NumSv_P_Mil_TipEsc = models.IntegerField
    DtSv_V_Mil_TipEsc = models.DateField
    NumSv_V_Mil_TipEsc = models.IntegerField

class Dispensa(models.Model):
    Desc_Disp = models.CharField(max_length=30)
    "Militares = models.ManyToManyField(Militar)"

class Militar_Dispensa(models.Model):
    Id_Mil = models.ForeignKey(Militar, on_delete=models.CASCADE)    
    Id_Disp = models.ForeignKey(Dispensa, on_delete=models.CASCADE)
    Begin_Mil_Disp = models.DateField
    End_Mil_Disp = models.DateField
    
class Matriz(models.Model):
    Id_SubTipEsc = models.ForeignKey(SubTipoEscala, on_delete=models.CASCADE)    
    Dt_Matriz = models.DateField
    NumMil_Matriz = models.IntegerField
    IsHolyday_Matriz = models.BooleanField
    "Servicos = models.ManyToManyField(Militar)"

class Servico(models.Model):
    Id_Mil = models.ForeignKey(Militar, on_delete=models.CASCADE)    
    Id_Matriz = models.ForeignKey(Matriz, on_delete=models.CASCADE)