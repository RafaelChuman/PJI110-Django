from datetime import time
from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields
from django.forms.models import ModelForm
import django.forms.utils
import django.forms.widgets
from django.utils.timezone import datetime, now

from PJI110.models import SU
from PJI110.models import PostGrad
from PJI110.models import Militar
from PJI110.models import Dispensa
from PJI110.models import Militar_Dispensa
from PJI110.models import Militar_Tipo, TipoEscala, SubTipoEscala

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

class DispensaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.Id_PG.Nome_PG + " " + obj.NomeG_Mil)

class Militar_DispensaForm(forms.ModelForm):
    Id_Disp = forms.ModelChoiceField(queryset=Dispensa.objects.all(), to_field_name="id" )
    Id_Mil = DispensaModelChoiceField(queryset=Militar.objects.select_related("Id_PG").filter(Vsb_Mil = True).order_by("-Id_PG", "NomeG_Mil"), to_field_name="id")
    Begin_Mil_Disp = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))
    End_Mil_Disp = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(Militar_DispensaForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['Begin_Mil_Disp'] = self.instance.Begin_Mil_Disp.isoformat()
            self.initial['End_Mil_Disp'] = self.instance.End_Mil_Disp.isoformat()
            

    class Meta:
        model = Militar_Dispensa
        fields = ("Id_Disp","Id_Mil", "Begin_Mil_Disp", "End_Mil_Disp" )

class Militar_TipoForm(forms.ModelForm):
    Id_Mil = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'ModelMultipleChoiceField'}), queryset=Militar.objects.all(), to_field_name="id" )
    Id_TipEsc = forms.ModelChoiceField(queryset=SubTipoEscala.objects.all(), to_field_name="id")
    DtSv_P_Mil_TipEsc = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    NumSv_P_Mil_TipEsc = forms.IntegerField(initial=0)
    DtSv_V_Mil_TipEsc = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    NumSv_V_Mil_TipEsc = forms.IntegerField(initial=0)


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(Militar_TipoForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['DtSv_P_Mil_TipEsc'] = self.instance.DtSv_P_Mil_TipEsc.isoformat()
            self.initial['DtSv_V_Mil_TipEsc'] = self.instance.DtSv_V_Mil_TipEsc.isoformat()
            

    class Meta:
        model = Militar_Tipo
        fields = ("Id_Mil","Id_TipEsc", "DtSv_P_Mil_TipEsc", "NumSv_P_Mil_TipEsc", "DtSv_V_Mil_TipEsc", "NumSv_V_Mil_TipEsc")       

