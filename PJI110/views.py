import re
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.views.generic import ListView

from PJI110.forms import MilitarForm
from PJI110.models import Militar



   
def getdata(request):
    militarList = Militar.objects.select_related("Id_SU", "Id_PG")
          
    return render(request, "PJI110/militares.html", {'militarList':militarList})

def Home(request):
    return render(request, "PJI110/home.html")


def escala(request):
   return render(request, "PJI110/escala.html")

def dispensa(request):
    return render(request, "PJI110/dispensa.html")     
    
def matriz(request):
    return render(request, "PJI110/matriz.html")       
