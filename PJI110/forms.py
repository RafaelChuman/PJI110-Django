from django import forms
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
    class Meta:
        model = Militar
        fields = ("NomeG_Mil","Nome_Mil", "DtNsc_Mil", "DtPrac_Mil", "DtProm_Mil", "Vsb_Mil", "Id_SU", "Id_PG", )

