
import re
import sys
from django.core.checks import messages
from django.forms.fields import NullBooleanField
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import datetime, now
from django.http import HttpResponse
from django.views.generic import ListView
from django import forms
from django.http import Http404

from django.http import HttpResponseRedirect
from django.urls import reverse

from PJI110.forms import Militar_TipoForm, MilitarForm, SubTipoEscalaForm, Militar_TipoEditForm
from PJI110.forms import Militar_DispensaForm
from PJI110.models import Militar, PostGrad, SU, TipoEscala
from PJI110.models import Dispensa, Militar_Dispensa
from PJI110.models import Militar_Tipo, SubTipoEscala


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
    
    PageTitle = ""
    
    if Id_Mil != 0:
        militar = get_object_or_404(Militar, pk=Id_Mil) 
        form = MilitarForm(request.POST or None, instance=militar)         

        PageTitle = "Editar " + militar.NomeG_Mil
    else:
        PageTitle = "Adicionar Novo Militar"
        
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
        'form': form,
        'PageTitle': PageTitle
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

                        return HttpResponseRedirect(reverse('militares'))

    militarList = Militar.objects.select_related("Id_SU", "Id_PG").filter(Vsb_Mil = False)


    context = {
        "object": militarList
    }    
        
    return render(request, "PJI110/militarHidden.html", {'militarList':militarList})
   
def MilitarSearch(request, *args, **kwargs):
    
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

    militarList = Militar.objects.select_related("Id_SU", "Id_PG").filter(Vsb_Mil = True)
    
            
    context = {
        'militarList':militarList
    }    
      
    return render(request, "PJI110/militares.html", context)

def Home(request):
    return render(request, "PJI110/home.html")

def EscalaDelMil(request, MilId, TipEscID):
    Militar_Tipo_Object =  Militar_Tipo.objects.get(Id_Mil = MilId, Id_TipEsc = TipEscID)
    Militar_Tipo_Object.delete()

def escalaEdit(request, id_Militar, id_TipoEscala):
    
    PageTitle = ""
    
    MilitarTipo_Object = get_object_or_404(Militar_Tipo, Id_Mil = id_Militar, Id_TipEsc = id_TipoEscala) 
    form = Militar_TipoEditForm(request.POST or None, instance=MilitarTipo_Object) 



    PageTitle = "Editar " + MilitarTipo_Object.Id_Mil.NomeG_Mil

    if request.method == 'POST':
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(reverse('escala'))
        else:
            print(form.errors)

    context = {
        'form': form,
        'MilitarTipo_Object':MilitarTipo_Object,
        'PageTitle': PageTitle
    }
    
    # return HttpResponseRedirect(reverse('escalaEdit', args=(id_Militar,id_TipoEscala,)))
    return render(request, "PJI110/escalaEdit.html", context)  

def EscalaAdd(request, SubTipEscID):
    
    PageTitle = "Editar Escala" 
    
    if request.method == 'POST':

        form = Militar_TipoForm(request.POST, request.FILES)

        # if form.is_valid():

        Id_SubTipoEscalaInstance = SubTipoEscala.objects.get(id = form.data['Id_TipEsc'])

        for militar in request.POST.getlist('Id_Mil'):
            if Militar_Tipo.objects.filter(Id_Mil=militar,Id_TipEsc =  Id_SubTipoEscalaInstance.Id_TipEsc).count() == 0:
                Militar_Tipo.objects.create(
                    Id_Mil = Militar.objects.get(id=militar),
                    Id_TipEsc = Id_SubTipoEscalaInstance.Id_TipEsc,
                    # DtSv_P_Mil_TipEsc = form.data['DtSv_P_Mil_TipEsc'],
                    # NumSv_P_Mil_TipEsc = form.data['NumSv_P_Mil_TipEsc'],
                    # DtSv_V_Mil_TipEsc =form.data['DtSv_V_Mil_TipEsc'],
                    # NumSv_V_Mil_TipEsc = form.data['NumSv_V_Mil_TipEsc']
                )

        # profile = form.save(commit=False)
        # profile.user = request.user
        # profile.post = request.POST
        # profile.save()

        # form.save_m2m()

        return HttpResponseRedirect(reverse('escala'))
        # else:
        #     print(form.errors)
    else:
      
        form = Militar_TipoForm()

    context = {
        'form': form,
        'PageTitle': PageTitle
    }
    
    return render(request, "PJI110/escalaAdd.html", context)

def escala(request, *args, **kwargs):
    
    MilitaresList = 0


    if request.session.get('SubTipoEscalaId') != 0: TipoEscalaId =  request.session.get('SubTipoEscalaId')

    

    if len(request.GET) > 0:
        for action in request.GET:
            if action == "EscalaSelect":
                MilitaresList = TipoEscala.objects.get(id =  request.GET['EscalaSelect'])
                MilitaresList = MilitaresList.Militares_TipoEscala.all()
                # MilitaresList = MilitaresList.filter(Id_Mil__Vsb_Mil = True)
                # filter(Id_TipEsc =  request.GET['EscalaSelect'])

                request.session['SubTipoEscalaId'] = request.GET['EscalaSelect']
            else:
                if action == "EscalaAdd":
                   return EscalaAdd(request, 0)
                else:                          
                    if action == "EscalaMannage":
                       return redirect("../tipoEscala")
                    else:
                        if action == "MilitarEdit":
                            return escalaEdit(request, request.GET['MilitarEdit'], TipoEscalaId)             
                        else:                          
                            if action == "MilitarDel":
                                EscalaDelMil(request, request.GET['MilitarDel'], TipoEscalaId)
        
                 
    
    
    # DispensaList = Militar_Dispensa.objects.select_related("Id_Mil", "Id_Disp").select_related("Id_Mil__Id_PG")
    SubTipoEscalaList = SubTipoEscala.objects.all()

    context = {             
        'SubTipoEscalaList':SubTipoEscalaList,
        'MilitaresList':MilitaresList,
        'TipoEscalaId':TipoEscalaId,
    } 

    return render(request, "PJI110/escala.html", context)  

def tipoEscalaAdd(request, id_SubtipoEscala):
    
    PageTitle = ""
    
    if id_SubtipoEscala != 0:
        SubTipoEscala_Object = get_object_or_404(SubTipoEscala, pk=id_SubtipoEscala) 
        form = SubTipoEscalaForm(request.POST or None, instance=SubTipoEscala_Object)         

        PageTitle = "Editar " + SubTipoEscala_Object.Nome_SubTipEsc
    else:
        PageTitle = "Adicionar Novo SubTipSV"
        
        SubTipoEscala_Object = SubTipoEscala()
        form = SubTipoEscalaForm(request.POST or None)

    

    if request.method == 'POST':
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(reverse('tipoEscala'))
        else:
            print(form.errors)

    context = {
        'form': form,
        'PageTitle': PageTitle
    }
    
    return render(request, "PJI110/tipoEscalaAdd.html", context)

#Os Parâmetros ARGS e KWARGS são parâmetros Curinga e podem conter qualquer valor
#Função para Listar Todos os Tipos de Escala de Serviço e Editar Sub Tipos de Escala de Serviço
def tipoEscala(request, *args, **kwargs):
    
    #Inicializando a variável para Listar de Todos os Tipos de Escla de Serviço
    SubTipoEscalaList = 0
 
    #Verifica se o Evento da Página é o GET. O Método GET é importante, porque todas os botões da página usam o método GET
    if len(request.GET) > 0:

        for action in request.GET:
            #Evento de Clicar em um Campo da Tabela para mostrar os SubTipos de Escala de Serviço
            if action == "EscalaSelect":
                #O Metodo Objects.Get retorna uma Instância de TipoEscala. Essa Instância é usada para Selecionar os SubTipos de Escala de Serviço
                SubTipoEscalaList = TipoEscala.objects.get(id =  request.GET['EscalaSelect'])
                SubTipoEscalaList = SubTipoEscalaList.subtipoescala_set.all()
            else:
                if action == "SubTipoEscalaAdd":
                   return tipoEscalaAdd(request, 0)
                else:   
                    if action == "SubtipoEscalaEdit":
                        return tipoEscalaAdd(request, request.GET['SubtipoEscalaEdit'])                       
                    else:
                        if action == "SubtipoEscalaDel":
                            #Comando para Deletar um SubTipo de Escala de Serviço. O Id é passado pelo Código HTML e Resgatado pelo Método GET
                            SubTipoEscala.objects.get(id = request.GET['SubtipoEscalaDel']).delete()
                      
    #Comando para Selecionar Todos os Tipo de Escala de Serviço    
    TipoEscalaList = TipoEscala.objects.all()

    #Variável Context Contém Todas as Informações que serão renderizadas no Formulario HTML
    context = {             
        'TipoEscalaList':TipoEscalaList,
        'SubTipoEscalaList':SubTipoEscalaList,
    } 

    #Método Render força a criação da Página com os dados criados nesta Função
    return render(request, "PJI110/tipoEscala.html", context)  

def dispensaSearch(request, *args, **kwargs):
    
    if len(request.GET) > 0:
        for action in request.GET:
            if action == "DispensaAdd":
                return DispensaAdd(request, 0)
            else:
                if action == "DispensaEdit":
                    return DispensaAdd(request, request.GET['DispensaEdit'])
                else:                          
                    if action == "DispensaDel":
                        return DispensaDel(request, request.GET['DispensaDel'])
    
    # DispensaList = Militar_Dispensa.objects.select_related("Id_Mil", "Id_Disp").select_related("Id_Mil__Id_PG")
    DispensaList = Militar_Dispensa.objects.filter(Id_Mil__Vsb_Mil = True, End_Mil_Disp__gte = datetime.now())

    
    context = {             
        'DispensaList':DispensaList
    } 

    return render(request, "PJI110/dispensa.html", context)     
    
def DispensaDel(request, Id_Disp):
    
    if Id_Disp != 0:
        Militar_DispensaList = get_object_or_404(Militar_Dispensa, pk=Id_Disp)
        
        if Militar_DispensaList is not None:  
            Militar_DispensaList.delete()
            
    return HttpResponseRedirect(reverse('dispensa'))

def DispensaAdd(request, Id_Disp):
    
    PageTitle = ""
    
    if Id_Disp != 0:
        Militar_DispensaList = get_object_or_404(Militar_Dispensa, pk=Id_Disp) 
        form = Militar_DispensaForm(request.POST or None, instance=Militar_DispensaList)         

        PageTitle = "Editar " + Militar_DispensaList.Id_Mil.NomeG_Mil
    else:
        PageTitle = "Adicionar Nova Dispensa"
        
        Militar_DispensaList = Militar_Dispensa()
        form = Militar_DispensaForm(request.POST or None)
   

    if request.method == 'POST':
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(reverse('dispensa'))
        else:
            print(form.errors)

    context = {
        'form': form,
        'PageTitle': PageTitle
    }
    
    return render(request, "PJI110/dispensaAdd.html", context)

def matriz(request):
    return render(request, "PJI110/matriz.html")       
