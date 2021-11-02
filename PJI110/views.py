
from datetime import date, timedelta
import re
import sys
from django.core.checks import messages
from django.forms.fields import NullBooleanField
from django.forms.forms import Form
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import datetime, now
from django.http import HttpResponse
from django.views.generic import ListView
from django import forms
from django.http import Http404

from django.db.models.query import QuerySet
from django.db.models import Prefetch

from django.http import HttpResponseRedirect
from django.urls import reverse

from PJI110.forms import MatrizForm, Militar_TipoForm, MilitarForm, SubTipoEscalaForm, Militar_TipoEditForm
from PJI110.forms import Militar_DispensaForm
from PJI110.forms import MatrizForm, MonthOfMatrizForm
from PJI110.forms import ServicoForm
from PJI110.models import Militar, PostGrad, SU, TipoEscala
from PJI110.models import Dispensa, Militar_Dispensa
from PJI110.models import Militar_Tipo, SubTipoEscala
from PJI110.models import Matriz 
from PJI110.models import Servico 


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


def IsHolyday(self, *args, **kwargs):

    if self is None: return False

    if self.weekday() > 4:
        return True
    else:
        return False

def matrizAdd(request, Id_Matriz):
    PageTitle = 'Add Matriz SV'

    if request.method == 'POST':


        form = MatrizForm(request.POST, request.FILES)

        if form.is_valid():
            DateBegin = form.cleaned_data['DtBegin_Matriz']
            DateEnd = form.cleaned_data['DtEnd_Matriz']
            Id_SubTipEsc = form.cleaned_data['Id_SubTipEsc']
            NumMil_Matriz = form.cleaned_data['NumMil_Matriz']

            while DateBegin <= DateEnd:
                if Matriz.objects.filter(Id_SubTipEsc=Id_SubTipEsc, Dt_Matriz = DateBegin).count() == 0:
                    Matriz.objects.create(
                            Id_SubTipEsc = Id_SubTipEsc,
                            Dt_Matriz = DateBegin,
                            NumMil_Matriz = NumMil_Matriz,
                            IsHolyday_Matriz = IsHolyday(DateBegin)
                        )
                DateBegin = DateBegin + timedelta(days=1)     


        return HttpResponseRedirect(reverse('matriz'))
    else:
        form = MatrizForm()

    context = {          
        'form':form,
        'PageTitle': PageTitle
    } 

    return render(request, "PJI110/matrizAdd.html", context)   


def addMonths(dt, months = 0):
    new_month = months + dt.month
    year_inc = 0
    if new_month>12:
        year_inc +=1
        new_month -=12
    return dt.replace(month = new_month, year = dt.year+year_inc)

def matriz(request):

    PageTitle = 'Matriz SV'

    if len(request.GET) > 0:
        for action in request.GET:
            if action == "MatrizASearch":
                MonthOfSearch = request.GET['MatrizASearch']
                MonthOfMatrix = MonthOfMatrizForm(request.POST or None, instance=MonthOfSearch)
            else:
                if action == "MatrizAdd":
                    return matrizAdd(request, 0)
                else:
                    if action == "MatrizEdit":
                        return matrizAdd(request, request.GET['MatrizEdit'])
                    # else:                          
                    #     if action == "MatrizDel":
                            #return matrizDel(request, request.GET['MatrizDel'])
    else:
        MonthOfSearch= datetime.now().month
        MonthOfMatrix = MonthOfMatrizForm()
        
    # DateBegin = datetime(datetime.now().year, MonthOfSearch, 1)
    # DateEnd =  addMonths(DateBegin, 1)

    DateBegin = datetime(datetime.now().year, MonthOfSearch -1, 1)
    DateEnd =  addMonths(DateBegin, 1)

    MatrizList = Matriz.objects.filter(Dt_Matriz__range=[DateBegin, DateEnd]).order_by('Dt_Matriz', 'Id_SubTipEsc')
     
    SubTipoEscalaList = Matriz.objects.values('Id_SubTipEsc__Nome_SubTipEsc').order_by('Id_SubTipEsc').distinct()

    ListDate = list()
    ListEscala = list()

    if len(MatrizList) > 0:
        x = DateBegin
       
        while x <= DateEnd:

            ListEscala = list()
            ListEscala.append(x.strftime("%d-%a"))

            for SubtipItem in SubTipoEscalaList:
                
                MatrizFor = MatrizList.filter(Dt_Matriz = x, Id_SubTipEsc__Nome_SubTipEsc = SubtipItem['Id_SubTipEsc__Nome_SubTipEsc'])
                
                if MatrizFor.count() > 0:
                    for ItemOfMatriz in MatrizFor:
                        ListEscala.append([ItemOfMatriz.NumMil_Matriz,ItemOfMatriz.IsHolyday_Matriz])    
                else:     
                    ListEscala.append([0, False]) 
                    
            
            ListDate.append(ListEscala)
            x = x + timedelta(days=1)
    else:
        x=0
        

    context = {  
        'PageTitle':PageTitle,
        'SubTipoEscalaList':SubTipoEscalaList,
        'ListDate':ListDate,
        'MonthOfMatriz':MonthOfMatrizForm,
        
    } 

    return render(request, "PJI110/matriz.html", context, )  


def AppendMilitarIntoServico(ListMilitarDispensado, ListMilitaresServico, ListServico, ListTemp, ItemMatrizEscala):
    
    #Indice Começa em 0, porque é o Primeiro Militar da Lista é o próximo a ser escalado
    xV = 0
    #Condição para não Adicionar o Militar que Esta Dispensado nesse Dia
    while(ListMilitarDispensado.filter(Id_Mil = ListMilitaresServico[xV].id).count() >0):
        #Se o militar não pode ser Escalado, então pegamos o Próximo da Lista Disponível
        xV = xV + 1

    #Condição para Verificar se o Militar Ja Está de Serviço em Outro Tipo de Servço
    #A Condição Deverá Vericar 2 Dias Antes e 2 Dias Depois. Pois 48h é o Intervalo Mínimo entre 1 Serviço e Outro
    DtBegin = ItemMatrizEscala.Dt_Matriz - timedelta(days=2)
    DtEnd = ItemMatrizEscala.Dt_Matriz
    while(Servico.objects.filter(Id_Matriz__Dt_Matriz__range=[DtBegin,DtEnd], Id_Mil = ListMilitaresServico[xV].Id_Mil).count() > 0):
        xV = xV + 1 

    #Condição para Verificar se o Militar Já Está de Serviço Na Escala Preta
    #A Condição Deverá Verificar 2 dias Antes. Pois o Intervalo Mínimo de 1 Serviço para Outro é também de 48h
    NumListSV = len(ListServico)
    y = NumListSV - 2
    reset = False
    if(y >= 0):
        while(y < NumListSV):
            for Item in ListServico[y][2]:#ListServico[y][2] = 3º Posição, Pois o Método Append na linha 623 Adiciona ListTemp na 3ª Posição
                while(Item[0] == ListMilitaresServico[xV]):#Item[0] = 1ª Posição, está seguindo a Ordem do Método Append 
                    xV = xV + 1 
                    reset = True

            #Essa Condição é Nescessária, porque é um ERRo Lógico não verificar (Os 2 Dias Antes) para o Novo Militar Selecionado
            #Sem Essa Condição, após sair do While o Código adiciona y + 1, então só estariamos verificando 1 Dia Antes
            if (reset): 
                y = NumListSV - 2
                reset = False
            else:
                y = y + 1        

    #Adiciona o Militar Na Lista de Escalados.
    ListTemp.append([ListMilitaresServico[xV].id, ItemMatrizEscala.id]) 

    #Retiramos o Militar Escalado e Colocamos no final da Fila, pois ele passa a ser o Mais folgado na Escala de Serviço  
    ListMilitaresServico.append(ListMilitaresServico[xV]) 
    ListMilitaresServico.pop(xV)

def Home(request):

    PageTitle = 'Escala de SV 1º B Av Ex'
    MatrizEscala = ""
    SubTipoEscalaList = ""
    #Essa Lista Será Exibida na Página e Após ser Homologada Será Salva na Base de Dados
    ListServico = list()
    
    #Para Calcular a escala de Serviço precisamos:    
    '''
    1º Selecionar a Data que desejamos montar a escala de Serviço
    '''
    '''
    2º O Sistema Vai Mostrar uma Tabela com os Dados dos Militares que estarão de Serviço
    '''
    '''
    3º O Adminsitrador vai homologar os dados salvando na Tabela de SV
    '''
    '''
    4º Quando Excluir um Militar da Escala de Serviço (Tabela de Dispensa) - Verificar se Esse Militar Esta na Escala de SV Salva
    '''
    '''
    5º Caso Positivo o Sistema deverá Excluir todos os Serviços Posteriores (Excluit por SV e não somente o TipoEscalaSV)
    '''
    '''
    6º Novamente o Adm deverá Iniciar do Passo 1º
    '''
    if request.method == 'POST':
        form = ServicoForm(request.POST, request.FILES)

        if form.is_valid():
            DateBegin = form.cleaned_data['DtBegin_Servico']
            DateEnd = form.cleaned_data['DtEnd_Servico']
            Id_TipEscForm = form.cleaned_data['Id_TipEsc']

            #Atualiza a Caixa de Pesquisa de Acorodo com o Filtro do Usuário
            SubTipoEscalaList  = SubTipoEscala.objects.filter(Id_TipEsc = Id_TipEscForm)
            
            #Pesquisar a Matriz de Acordo com o Filtro do Usuário
            MatrizEscala =  Matriz.objects.filter(Dt_Matriz__range=[DateBegin, DateEnd], Id_SubTipEsc__Id_TipEsc = Id_TipEscForm)
            
            ListMatrizEscala = list()
            #Listar Todos os Itens da Matriz que não foram inseridos na Tabela de Serviço
            ServicoEscala = Servico.objects.filter(Id_Matriz__Dt_Matriz__range=[DateBegin, DateEnd])
            for ItemMatrizEscala in MatrizEscala:
                if(ServicoEscala.filter(Id_Matriz = ItemMatrizEscala.id).count() == 0): ListMatrizEscala.append(ItemMatrizEscala)
            
            #Selecionar Todos os Militares que Concorrem a Escala de Serviço. Faço uma Conversão Para List, porque  Militar No Topo da Fila será o Proximo para o Serviço
            #Caso o Militar Esteja Dispensado ele Continuará no Topo da Lista até a Dispensa acabar e ele ser escalado
            #Quando o Sistema For Reiniciado a Ordenação da Data de Serviço Fará que o Militar Seja o 1º da Lista Novamente.
            ListMilitaresServicoPreta  = list(Militar_Tipo.objects.filter(Id_TipEsc = Id_TipEscForm).order_by('DtSv_P_Mil_TipEsc', "NumSv_P_Mil_TipEsc"))
            ListMilitaresServicoVermelha  = list(Militar_Tipo.objects.filter(Id_TipEsc = Id_TipEscForm).order_by('DtSv_V_Mil_TipEsc', "NumSv_V_Mil_TipEsc"))

            #Atribuir Cada Militar Para Seu respectivo Dia da Escala
            for ItemMatrizEscala in ListMatrizEscala:
                
                ListTemp = list()

                #Lista de Todos os Militares Dispensados Nessa Data
                ListMilitarDispensado = Militar_Dispensa.objects.filter(Begin_Mil_Disp__gte = ItemMatrizEscala.Dt_Matriz, End_Mil_Disp__lte = ItemMatrizEscala.Dt_Matriz)

                #Para Cada Item Da Matriz Deve Escalar Um Militar
                x = 0
                NumMil = ItemMatrizEscala.NumMil_Matriz
                while x <  NumMil:
                    if ItemMatrizEscala.IsHolyday_Matriz:
                        
                        AppendMilitarIntoServico(ListMilitarDispensado, ListMilitaresServicoVermelha, ListServico, ListTemp, ItemMatrizEscala)
                  
                    else:

                        AppendMilitarIntoServico(ListMilitarDispensado, ListMilitaresServicoPreta, ListServico, ListTemp, ItemMatrizEscala)                       
                    
                    x = x + 1
                #Adiciona Todos Os Serviços do SubTipo da Escala Concatenados em Vetores. (Esse Concatenação é importante, pois será usado na iteração For-For)
                ListServico.append([ItemMatrizEscala.Dt_Matriz, ItemMatrizEscala.Id_SubTipEsc, ListTemp])        
    else:
        form = ServicoForm()

        #Recupera o Primerio Tipo Escala para inserir no FORM.
        filtroTipoEscala = TipoEscala.objects.all()[:1][0]
        ServicoList = Servico.objects.filter(Id_Matriz__Id_SubTipEsc__Id_TipEsc = filtroTipoEscala).order_by('-Id_Matriz__Dt_Matriz')[:5]

        #Caso não Exista Serviços na Data da data padrão será HOJE. Senão a Data Padrão será a data do Ultimo Serviço
        if ServicoList.count() > 0:           
            form['DtBegin_Servico'].value = datetime.now
        else:
            form['DtBegin_Servico'].value = ServicoList[0].Id_Matriz.DtMatriz   

        

    context = {  
        'PageTitle':PageTitle,
        'MatrizEscala':MatrizEscala,
        'SubTipoEscalaList': SubTipoEscalaList,
        'ListServico':ListServico,
        'form':form,        
    } 

    return render(request, "PJI110/home.html", context) 
