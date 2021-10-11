import re
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

def militarAdd(request, Id_Mil):
    
    if Id_Mil != 0:
        militar = get_object_or_404(Militar, pk=Id_Mil)
        form = MilitarForm(None, instance=militar)        
    else:
        form =  MilitarForm()

    
    if request.method == 'POST':
        form = MilitarForm(request.POST, instance=militar)
        # Create a form instance and populate it with data from the request (binding):
        # form = MilitarForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            form.save()
            form =  MilitarForm()

    context = {
        'form': form
    }
    
    return render(request, "PJI110/militarAdd.html", context)

def militarHidden(request, *args, **kwargs):
    return render(request, "PJI110/militarHidden.html")
   
def getdata(request, *args, **kwargs):
    if len(request.GET)>0:
        for action in request.GET:
            if action == "MilitarAdd":
                return militarAdd(request, 0)
            else:
                if action == "MilitarEdit":
                    return militarAdd(request, request.GET['MilitarEdit'])
                else:    
                    if action == "MilitarHidden":
                        return render(request, "PJI110/militarHidden.html")

    militarList = Militar.objects.select_related("Id_SU", "Id_PG").order_by("DtProm_Mil", "DtPrac_Mil", "DtNsc_Mil")
            
    return render(request, "PJI110/militares.html", {'militarList':militarList})

def Home(request):
    return render(request, "PJI110/home.html")


def escala(request):
   return render(request, "PJI110/escala.html")

def dispensa(request):
    return render(request, "PJI110/dispensa.html")     
    
def matriz(request):
    return render(request, "PJI110/matriz.html")       
