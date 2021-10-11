from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.widgets import Select
from PJI110.models import SU
from PJI110.models import PostGrad

class AddMilitar(forms.Form):
    NomeG = forms.CharField(max_length=20)
    Nome_Mil = forms.CharField(max_length=100)
    DtNsc_Mil = forms.DateField()
    DtPrac_Mil  = forms.DateField()
    DtProm_Mil = forms.DateField()
    Vsb_Mil = forms.BooleanField(initial=True)
    SU = forms.ModelChoiceField(queryset=SU.objects.all())

    def clean_NomeG(self):
        NomeG = self.cleaned_data['NomeG']

        if len(NomeG) > 20 or NomeG == "":
            raise ValidationError(_('Nome de Guerra Inválido'))

        return NomeG

    def clean_Nome_Mil(self):
        Nome_Mil = self.cleaned_data['NomeG']

        if len(Nome_Mil) > 100 or Nome_Mil == "":
            raise ValidationError(_('Nome do Militar Inválido'))

        return Nome_Mil        


