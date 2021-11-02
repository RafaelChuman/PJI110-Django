from datetime import date, time
from django import forms
from django.core.exceptions import DisallowedHost, ValidationError
from django.db.models.fields import DateField
from django.forms import fields
from django.forms.forms import Form
from django.forms.models import ModelForm
import django.forms.utils
import django.forms.widgets
from django.utils.timezone import datetime, now
from datetime import datetime

from PJI110.models import SU, Matriz
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


class Militar_TipoEditForm(forms.ModelForm):
    # Id_Mil = forms.ModelMultipleChoiceField(widget=forms.Select(), queryset=Militar.objects.all(), to_field_name="id" )
    # Id_TipEsc = forms.ModelChoiceField(queryset=TipoEscala.objects.all(), to_field_name="id")
    DtSv_P_Mil_TipEsc = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    NumSv_P_Mil_TipEsc = forms.IntegerField(initial=0)
    DtSv_V_Mil_TipEsc = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    NumSv_V_Mil_TipEsc = forms.IntegerField(initial=0)


    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(Militar_TipoEditForm, self).__init__(*args, **kwargs)

        if instance:
            # self.initial['Id_Mil'] = self.instance.Id_Mil
            # self.initial['Id_TipEsc'] = self.instance.Id_TipEsc
            self.initial['DtSv_P_Mil_TipEsc'] = self.instance.DtSv_P_Mil_TipEsc.isoformat()
            self.initial['DtSv_V_Mil_TipEsc'] = self.instance.DtSv_V_Mil_TipEsc.isoformat()
            # self.fields['Id_Mil'].widget.attrs['disabled'] = 'True'
            # self.fields['Id_Mil'].required = 'False'
            # self.fields['Id_TipEsc'].widget.attrs['disabled'] = 'True'
            # self.fields['Id_TipEsc'].required = 'False'
            
    class Meta:
        model = Militar_Tipo
        fields = ("DtSv_P_Mil_TipEsc", "NumSv_P_Mil_TipEsc", "DtSv_V_Mil_TipEsc", "NumSv_V_Mil_TipEsc")  


class SubTipoEscalaForm(forms.ModelForm):
    Nome_SubTipEsc = forms.CharField()
    Prioridade_SubTipEsc = forms.IntegerField()
    Id_TipEsc =  forms.ModelChoiceField(queryset=TipoEscala.objects.all(), to_field_name="id")

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(SubTipoEscalaForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['Nome_SubTipEsc'] = self.instance.Nome_SubTipEsc
            self.initial['Prioridade_SubTipEsc'] = self.instance.Prioridade_SubTipEsc
            self.initial['Id_TipEsc'] = self.instance.Id_TipEsc

    class Meta:
        model = SubTipoEscala
        fields = ("Nome_SubTipEsc","Prioridade_SubTipEsc", "Id_TipEsc")    

MONTH_CHOICES =(
    ("1","Janeiro"),
    ("2", "Fevereiro"),
    ("3", "Março"),
    ("4", "Abril"),
    ("5", "Maio"),
    ("6", "Junho"),
    ("7", "Julho"),
    ("8", "Agosto"),
    ("9", "Setebro"),
    ("10", "Outubro"),
    ("11", "Novebro"),
    ("12", "Dezembro"),
)

class MonthOfMatrizForm(forms.Form):
    DateOfMatriz = forms.ChoiceField(choices = MONTH_CHOICES, initial = datetime.now().month)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(MonthOfMatrizForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['MonthOfMatrizForm'] = self.instance.MonthOfMatrizForm




class MatrizForm(forms.Form):

    Id_SubTipEsc =  forms.ModelChoiceField(queryset=SubTipoEscala.objects.all(), to_field_name="id")
    DtBegin_Matriz = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    DtEnd_Matriz = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    NumMil_Matriz =  forms.IntegerField()
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(MatrizForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['Id_SubTipEsc'] = self.instance.Id_SubTipEsc
            self.initial['DtBegin_Matriz'] = self.instance.DtBegin_Matriz.isoformat()
            self.initial['DtEnd_Matriz'] = self.instance.DtEnd_Matriz.isoformat()
            self.initial['NumMil_Matriz'] = self.instance.NumMil_Matriz

class ServicoForm(forms.Form):

    Id_TipEsc =  forms.ModelChoiceField(queryset = TipoEscala.objects.all(), to_field_name="id")
    DtBegin_Servico = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)
    DtEnd_Servico = forms.DateField(widget = forms.DateInput(attrs = {'type': 'date'}), initial= datetime.now)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(ServicoForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['Id_TipEsc'] = self.instance.Id_TipEsc
            self.initial['DtBegin_Servico'] = self.instance.DtBegin_Servico.isoformat()
            self.initial['DtEnd_Servico'] = self.instance.DtEnd_Servico.isoformat()


    # class Meta:
    #     model = Matriz
    #     fields = ("Id_SubTipEsc","Dt_Matriz", "NumMil_Matriz", "IsHolyday_Matriz")    

    