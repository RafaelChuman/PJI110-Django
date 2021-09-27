import re
from django.utils.timezone import datetime
from django.shortcuts import render
from django.http import HttpResponse

def Home(request):
    return render(request, "PJI110/home.html")

def militares(request):
    return render(request, "PJI110/militares.html")

def escala(request):
   return render(request, "PJI110/escala.html")

def dispensa(request):
    return render(request, "PJI110/dispensa.html")     
    
def matriz(request):
    return render(request, "PJI110/matriz.html")       
