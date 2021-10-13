import re
import sys
from django.core.checks import messages
from django.forms.fields import NullBooleanField
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.views.generic import ListView
from django import forms

from django.http import HttpResponseRedirect
from django.urls import reverse

from PJI110.formsPadrao import MilitarForm
from PJI110.models import Militar
from PJI110.models import PostGrad
from PJI110.models import SU


def militarDel(request, Id_Mil):
    
    if Id_Mil != 0:
        militar = get_object_or_404(Militar, pk=Id_Mil)
        
        if militar is not None:  
            militar.Vsb_Mil = False
            militar.save()
    context = {
        "object": militar
    }
            
    return HttpResponseRedirect(reverse('militares'))



def militarAdd(request, Id_Mil):
    
    if Id_Mil != 0:
        militar = get_object_or_404(Militar, pk=Id_Mil) 
        form = MilitarForm(request.POST or None, instance=militar)         
    else:
        militar = Militar()
        form = MilitarForm(request.POST or None)

    

    if request.method == 'POST':
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(reverse('militares'))
        else:
            print(form.errors)

    context = {
        'form': form
    }
    
    return render(request, "PJI110/militarAdd.html", context)




def militarHidden(request, *args, **kwargs):

    if len(request.GET) > 0:
         for action in request.GET:
            if action == "MilitarReact":
                if request.GET['MilitarReact'] != 0:
                    militar = get_object_or_404(Militar, pk=request.GET['MilitarReact'])
                    
                    if militar is not None:
                        militar.Vsb_Mil = True
                        militar.save()

    militarList = Militar.objects.select_related("Id_SU", "Id_PG").filter(Vsb_Mil = False).order_by("DtProm_Mil", "DtPrac_Mil", "DtNsc_Mil")

    context = {
        "object": militarList
    }    
        
    return render(request, "PJI110/militarHidden.html", {'militarList':militarList})
   
def getdata(request, *args, **kwargs):
    
    if len(request.GET) > 0:
        for action in request.GET:
            if action == "MilitarAdd":
                return militarAdd(request, 0)
            else:
                if action == "MilitarEdit":
                    return militarAdd(request, request.GET['MilitarEdit'])
                else:                          
                    if action == "MilitarDel":
                        return militarDel(request, request.GET['MilitarDel'])
                    else:  
                        if action == "MilitarHidden":
                            return redirect("../militarHidden")

    militarList = Militar.objects.select_related("Id_SU", "Id_PG").filter(Vsb_Mil = True).order_by("DtProm_Mil", "DtPrac_Mil", "DtNsc_Mil")
            
    return render(request, "PJI110/militares.html", {'militarList':militarList})

def Home(request):
    return render(request, "PJI110/home.html")


def escala(request):
   return render(request, "PJI110/escala.html")

def dispensa(request):
    return render(request, "PJI110/dispensa.html")     
    
def matriz(request):
    return render(request, "PJI110/matriz.html")       
