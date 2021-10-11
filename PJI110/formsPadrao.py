from django import forms
import django.forms.utils
import django.forms.widgets

from PJI110.models import SU
from PJI110.models import PostGrad
from PJI110.models import Militar

class SUForm(forms.ModelForm):    
    class Meta:
        model = SU
        fields = ("Nome_SU",)
    
class PostGradForm(forms.ModelForm):    
    class Meta:
        model = PostGrad
        fields = ("Nome_PG",)
 
class MilitarForm(forms.ModelForm):    
    Id_PG = forms.ModelChoiceField(queryset= PostGrad.objects.all(), to_field_name="id")
    DtProm_Mil = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%Y'))
    DtPrac_Mil = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%Y'))
    DtNsc_Mil = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%Y'))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        super(MilitarForm, self).__init__(*args, **kwargs)

        if instance:
            self.initial['DtProm_Mil'] = self.instance.DtProm_Mil.isoformat()
            self.initial['DtPrac_Mil'] = self.instance.DtPrac_Mil.isoformat()
            self.initial['DtNsc_Mil'] = self.instance.DtNsc_Mil.isoformat()

    class Meta:
        model = Militar
        fields = ("NomeG_Mil","Nome_Mil", "DtNsc_Mil", "DtPrac_Mil", "DtProm_Mil", "Vsb_Mil", "Id_SU", "Id_PG", )

