from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms.models import ModelForm
import django.forms.utils
import django.forms.widgets

from PJI110.models import SU
from PJI110.models import PostGrad
from PJI110.models import Militar
from PJI110.models import Dispensa
from PJI110.models import Militar_Dispensa

class SUForm(forms.ModelForm):    
    class Meta:
        model = SU
        fields = ("Nome_SU",)
    
class PostGradForm(forms.ModelForm):    
    class Meta:
        model = PostGrad
        fields = ("Nome_PG",)

class DispensaForm(forms.ModelForm):
    class Meta:
        model = Dispensa
        fields = ("Desc_Disp",)
 
class MilitarForm(forms.ModelForm):    
    Id_PG = forms.ModelChoiceField(queryset = PostGrad.objects.all(), to_field_name="id")
    DtProm_Mil = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))
    DtPrac_Mil = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))
    DtNsc_Mil = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))
    Vsb_Mil = forms.BooleanField(widget = forms.HiddenInput(), required = False, initial=True)


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(MilitarForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['DtProm_Mil'] = self.instance.DtProm_Mil.isoformat()
            self.initial['DtPrac_Mil'] = self.instance.DtPrac_Mil.isoformat()
            self.initial['DtNsc_Mil'] = self.instance.DtNsc_Mil.isoformat()
            self.initial['Vsb_Mil'] = self.instance.Vsb_Mil
            

    class Meta:
        model = Militar
        fields = ("NomeG_Mil","Nome_Mil", "DtNsc_Mil", "DtPrac_Mil", "DtProm_Mil", "Vsb_Mil", "Id_SU", "Id_PG", )


    def clean_NomeG_Mil(self, *args, **kwargs):
       NomeG_Mil = self.cleaned_data.get("NomeG_Mil")    
       if NomeG_Mil is not None:
          return NomeG_Mil
       else:
           raise forms.ValidationError("Nome de Guerra do Militar Inválido")

class Militar_DispensaForm(forms.ModelForm):
    Id_Disp = forms.ModelChoiceField(queryset=Dispensa.objects.all(), to_field_name="id" )
    Id_Mil = forms.ModelChoiceField(queryset=Militar.objects.select_related("Id_PG").filter(Vsb_Mil = True), to_field_name="id")
    Begin_Mil_Disp = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))
    End_Mil_Disp = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(MilitarForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['Begin_Mil_Disp'] = self.instance.Begin_Mil_Disp.isoformat()
            self.initial['End_Mil_Disp'] = self.instance.End_Mil_Disp.isoformat()
            

    class Meta:
        model = Militar_Dispensa
        fields = ("Id_Disp","Id_Mil", "Begin_Mil_Disp", "End_Mil_Disp" )

