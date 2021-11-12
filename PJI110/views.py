
from datetime import date, timedelta
import re
import sys
from typing import List
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
from django.utils import timezone

from django.db.models.query import QuerySet
from django.db.models import Prefetch

from django.http import HttpResponseRedirect
from django.urls import reverse

from PJI110.forms import Militar_TipoForm, MilitarForm, SubTipoEscalaForm, Militar_TipoEditForm
from PJI110.forms import Militar_DispensaForm
from PJI110.forms import MatrizSelectForm, MatrizAddForm, MatrizDelForm, MatrizEditForm
from PJI110.forms import ServicoForm
from PJI110.models import Militar, PostGrad, SU, TipoEscala
from PJI110.models import Dispensa, Militar_Dispensa
from PJI110.models import Militar_Tipo, SubTipoEscala
from PJI110.models import Matriz 
from PJI110.models import Servico 

#Deletas Todos os Serviços apartir de uma Data Incial, Quando Alteramos um TipEscala
def servicoDel(DateBegin, IdMilitar):

    SubTipEscalaList = Militar_Tipo.objects.filter(Id_Mil = IdMilitar)

    if SubTipEscalaList.count != 0:
        for SubTipEscalaItem in SubTipEscalaList:
            ServicoSearchObject = Servico.objects.filter(Id_Matriz__Dt_Matriz__gte = DateBegin, Id_Matriz__Id_SubTipEsc__Id_TipEsc = SubTipEscalaItem.id)

            if ServicoSearchObject.count() != 0:
                for ServicoSearchItem in ServicoSearchObject:
                    ServicoSearchItem.delete()

#Deletas Todos os Serviços apartir de uma Data Incial
def servicoDel(DateBegin):

    ServicoSearchObject = Servico.objects.filter(Id_Matriz__Dt_Matriz__gte=DateBegin)

    if ServicoSearchObject.count() != 0:
        for ServicoSearchItem in ServicoSearchObject:
            ServicoSearchItem.delete()
                
        
    


#Função para Deletar um Militar a Partir de um ID
#O Militar não é Excluido, Mas alteramos sua Flag Visible para FALSE
def militarDel(request, IdMil):
    
    '''
    Ao Excluir um Militar devemos Retirar ele da Escala de Serviço. (Tabela Militar_Tipo)
    '''
    '''
    Ao Excluir o Militar Também Devemos Excluir Todos os Serviços que o Militar está escalado Apartir da Data Atual do Sistema
    '''

    if IdMil != 0:
        militar = get_object_or_404(Militar, pk=IdMil)
        
        if militar is not None:  

            #Exclui Todos Os Serviços do Militar. Também Excluimos Toda a escala em que o Militar Participa, pois ao retirar o Militar alteramos
            #A Folga de toda a escala
            servicoDel(DateBegin=datetime.now(), IdMilitar=IdMil)

            MilitarTipoList = Militar_Tipo.objects.filter(Id_Mil = IdMil)
            if MilitarTipoList.count() != 0:

                for MilitarTipoItem in MilitarTipoList:
                    MilitarTipoItem.delete() #Exclui o Militar da Escala de Serviço
            
            militar.Vsb_Mil = False
            militar.save()



    context = {
        "object": militar
    }
            
    return HttpResponseRedirect(reverse('militares'))

#Função para Adicionar/Atualizar o Militar. Se o Id Existir então atualizamos os Dados, Senão Inserimos um Militar Novo
def militarAdd(request, Id_Mil):
    
    PageTitle = ""
    
    if Id_Mil != 0:
        militar = get_object_or_404(Militar, pk=Id_Mil) 
        form = MilitarForm(request.POST or None, instance=militar) #Método Carrega o FORM com os dados do Militar        

        PageTitle = "Editar " + militar.NomeG_Mil
    else:
        PageTitle = "Adicionar Novo Militar"
        
        militar = Militar()
        form = MilitarForm(request.POST or None)    #Cria um FORM Novo
    
    if request.method == 'POST':
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(reverse('militares'))   #Após Salvar os Dados do Militar retornamos para a Página Inicial de Militares
        else:
            print(form.errors)

    context = {
        'form': form,
        'PageTitle': PageTitle
    }
    
    return render(request, "PJI110/militarAdd.html", context)

#Função para Restaurar/Reativar um Militar Excluido
def militarHidden(request, *args, **kwargs):

    if len(request.GET) > 0:
         for action in request.GET:
            if action == "MilitarReact":
                if request.GET['MilitarReact'] != 0:

                    militar = get_object_or_404(Militar, pk=request.GET['MilitarReact']) #Pesquisa e Recupera o Objeto Militar
                    
                    if militar is not None:
                        militar.Vsb_Mil = True  #Atualiza a Flag Visible para TRUE. A Flag Visible determina se o Militar Está Habilitado ou não
                        militar.save()

                        return HttpResponseRedirect(reverse('militares'))

    #Retorna Todos Os Miltiares Desabilitados
    militarList = Militar.objects.select_related("Id_SU", "Id_PG").filter(Vsb_Mil = False)

    context = {
        "militarList": militarList
    }    
        
    return render(request, "PJI110/militarHidden.html", context)
   
#Página Principal de Militares   
def MilitarSearch(request, *args, **kwargs):
    
    if len(request.GET) > 0:
        for action in request.GET:
            if action == "MilitarAdd":
                return militarAdd(request, 0)
            else:
                if action == "MilitarEdit":
                    return militarAdd(request, request.GET['MilitarEdit']) #O Id != 0 Determina a Função de Atualizar os dados do Militar
                else:                          
                    if action == "MilitarDel":
                        return militarDel(request, request.GET['MilitarDel'])
                    else:  
                        if action == "MilitarHidden":
                            return HttpResponseRedirect(reverse('militarHidden'))

    #Recupera todos os Militares que Estão Habilitados no Sistema
    militarList = Militar.objects.select_related("Id_SU", "Id_PG").filter(Vsb_Mil = True)
    
            
    context = {
        'militarList':militarList
    }    
      
    return render(request, "PJI110/militares.html", context)

 
#Função Para Desassociar um Militar de Um Tipo de Escala de Serviço
def EscalaDelMil(request, MilId, TipEscID):
   
    '''
    Ao Excluir Uma Associação de um Militar com Uma Escala de Serviço Devemos excluir todos os Serviços desse Militar Apartir da Data Atual do Sistema
    '''

    if MilId != 0 & TipEscID != 0:
        Militar_Tipo_Object =  Militar_Tipo.objects.get(Id_Mil = MilId, Id_TipEsc = TipEscID)
        
        if Militar_Tipo_Object is not None:  

            #Exclui Todos Os Serviços do Militar. Também Excluimos Toda a escala em que o Militar Participa, pois ao retirar o Militar alteramos
            #A Folga de toda a escala
            servicoDel(DateBegin=datetime.now(), IdMilitar=MilId)

            Militar_Tipo_Object.delete()
           
#Essa Função somente Altera os Dados De serviço da Tabela Militar_Tipo, como: Data do ultimo Serviço e Quantidade de Serviço Tirado
def escalaEdit(request, id_Militar, id_TipoEscala):
    
    '''
    Ao Editar Uma Associação de um Militar com Uma Escala de Serviço Devemos excluir todos os Serviços desse Militar Apartir da Data Atual do Sistema
    '''
    
    PageTitle = ""
    
    #Recupera o Objeto Militar_Tipo
    MilitarTipo_Object = get_object_or_404(Militar_Tipo, Id_Mil = id_Militar, Id_TipEsc = id_TipoEscala) 
    form = Militar_TipoEditForm(request.POST or None, instance=MilitarTipo_Object) 

    PageTitle = "Editar " + MilitarTipo_Object.Id_Mil.NomeG_Mil

    if request.method == 'POST':
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()  #Salva o Objeto Militar_Tipo. Os Dados São alterados no Form pelo Usuário

            #Exclui Todos Os Serviços do Militar. Também Excluimos Toda a escala em que o Militar Participa, pois ao retirar o Militar alteramos
            #A Folga de toda a escala
            servicoDel(DateBegin=datetime.now(), IdMilitar=form.cleaned_data['Id_Mil'])

            return HttpResponseRedirect(reverse('escala'))
        else:
            print(form.errors)

    context = {
        'form': form,
        'MilitarTipo_Object':MilitarTipo_Object,
        'PageTitle': PageTitle
    }
    
    return render(request, "PJI110/escalaEdit.html", context)  

#Adiciona uma Lista de Militares para uma Escala de Serviço no Model Militar_Tipo
#Esse Model é responsável por defir em qual escala de serviço o militar irá participar
def EscalaAdd(request, SubTipEscID):
    
    '''
    Ao Adicionar militares em uma Escala de Serviço, Devemos Limpar o Serviço calculado para o TipoEsc serviço que o Militar foi Adicionao
    '''

    PageTitle = "Editar Escala" 
    
    if request.method == 'POST':

        form = Militar_TipoForm(request.POST, request.FILES)

        Id_SubTipoEscalaInstance = SubTipoEscala.objects.get(id = form.data['Id_TipEsc'])

        #Iteração para Inserir Militar por Militar na Tabela Militar_Tipo
        for militar in request.POST.getlist('Id_Mil'):
            if Militar_Tipo.objects.filter(Id_Mil=militar,Id_TipEsc =  Id_SubTipoEscalaInstance.Id_TipEsc).count() == 0:
                #Salva o Militar e o Tipo de Escala no Model Militar_Tipo
                Militar_Tipo.objects.create(
                    Id_Mil = Militar.objects.get(id=militar),
                    Id_TipEsc = Id_SubTipoEscalaInstance.Id_TipEsc,
                )

                servicoDel(DateBegin=datetime.now(),id_Mil = militar)   #Limpa Todos os Serviços do TipEsc que o Militar Está inserido
                        
        return HttpResponseRedirect(reverse('escala'))
    else:
        form = Militar_TipoForm()

    context = {
        'form': form,
        'PageTitle': PageTitle
    }
    return render(request, "PJI110/escalaAdd.html", context)

#Tela Principal da Escala de Serviço. Exibe os Militares de acordo com a escala de serviço selecionada
def escala(request, *args, **kwargs):
    
    MilitaresList = 0

    #Ainformação de qual Escala de serviço foi selecionada esta gravada em uma Session
    if request.session.get('SubTipoEscalaId') != 0: TipoEscalaId =  request.session.get('SubTipoEscalaId')

    if len(request.GET) > 0:
        for action in request.GET:
            if action == "EscalaSelect":
                MilitaresList = TipoEscala.objects.get(id =  request.GET['EscalaSelect'])
                MilitaresList = MilitaresList.Militares_TipoEscala.all()

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
        
    SubTipoEscalaList = SubTipoEscala.objects.all()

    context = {             
        'SubTipoEscalaList':SubTipoEscalaList,
        'MilitaresList':MilitaresList,
        'TipoEscalaId':TipoEscalaId,
    } 

    return render(request, "PJI110/escala.html", context)  

#Adiciona um SubTipoEscala Herdado de um TipoEscala
def tipoEscalaAdd(request, id_SubtipoEscala):
    
    PageTitle = ""
    
    #Só realiza a pesquisa se o Id for válido
    if id_SubtipoEscala != 0:
        SubTipoEscala_Object = get_object_or_404(SubTipoEscala, pk=id_SubtipoEscala) 
        form = SubTipoEscalaForm(request.POST or None, instance=SubTipoEscala_Object)         

        PageTitle = "Editar " + SubTipoEscala_Object.Nome_SubTipEsc
    else: #Caso o Id seja inválido inicializa um Form Nulo, Logo iniciamos o processo de criar um novo SubTipoEscala
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

#Página principal para listar todas as dispensas cadastradas para os militares
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
    
    #Recupera todas as Dispensas que a Data da Dispensa tenha validade até a hora atual do sistema.
    #Caso a dispensa esteja com a Data Menor ela não deverá ser exibida, simplesmente porque a dispensa já acabou.
    #Não é nescessário excluir a dispensa, Inclusive é importante manter esse histório para futuros relatórios.
    #A dispensa somente será excluída se for por motivo de inserção erronea e o método de Update não for suficiente para corrigir
    DispensaList = Militar_Dispensa.objects.filter(Id_Mil__Vsb_Mil = True, End_Mil_Disp__gte = datetime.now())

    context = {             
        'DispensaList':DispensaList
    } 

    return render(request, "PJI110/dispensa.html", context)     
    
#Método de Excluisão da Dispensa. É uma página simples.    
def DispensaDel(request, Id_Disp, Id_Mil):
    
    '''
    Ao Exluir Uma Dispensa de Um Militar Devemos Excluir Todo o Serviço que o Militar Participa
    pois o Militar poderia estar de serviço nesse período dispensado (Não Tem como verificar se Ele Realmente Estaria de Serviço, 
    portanto recalculamos a Escala)
    '''

    if Id_Disp != 0:
        Militar_DispensaList = get_object_or_404(Militar_Dispensa, pk=Id_Disp)
        
        if Militar_DispensaList is not None:  
            #Exclui Todos Os Serviços do Militar. Também Excluimos Toda a escala em que o Militar Participa, pois ao retirar o Militar alteramos
            #A Folga de toda a escala
            servicoDel(DateBegin=Militar_DispensaList.Begin_Mil_Disp, IdMilitar=Id_Mil)

            Militar_DispensaList.delete()
            
    return HttpResponseRedirect(reverse('dispensa'))

#Método de Adicionar Dispensa. Também é uma página simples de um FormModel
def DispensaAdd(request, Id_Disp):
    
    PageTitle = ""
    
    '''
    Ao Adicionar Uma Dispensa em Um Militar Devemos verificar se o Militar Está de serviço Nesse Período.
    Caso o Militar esteja de Serviço Recalculamos toda a Escala de Serviço
    '''   

    #Condição para verificar se o Id é Válido. Caso seja Válido o Form terá função de Update, caso contrário será de Insert
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

            Begin_Mil_Disp  = form.cleaned_data['Begin_Mil_Disp']
            End_Mil_Disp  = form.cleaned_data['End_Mil_Disp']
            Id_Mil  = form.cleaned_data['Id_Mil']

            #Condição para Verificar se o Militar não está de serviço nessa data
            if Servico.objects.filter(Id_Matriz__Dt_Matriz__range = [Begin_Mil_Disp, End_Mil_Disp], Id_Mil = Id_Mil):
                #Exclui Todos Os Serviços do Militar. Também Excluimos Toda a escala em que o Militar Participa, pois ao retirar o Militar alteramos
                #A Folga de toda a escala
                servicoDel(DateBegin=Begin_Mil_Disp, IdMilitar=Id_Mil)

            return HttpResponseRedirect(reverse('dispensa'))
        else:
            print(form.errors)

    context = {
        'form': form,
        'PageTitle': PageTitle
    }
    
    return render(request, "PJI110/dispensaAdd.html", context)

#Método para Verificar se o Dia da Semana é Sábado ou Domingo. Porque Sábado e Domingo são Designados para Escalas Vermelhas.
#Os feriados devem ser incluídos 1 por 1 na Matriz. Infelizmente não podemos automatizar, porque o Batalhão deverá seguir o Calendário da Região Militar RM
#Nem sempre a Região Militar segue o feriado nascional, estadual ou municipal
def IsHolyday(self, *args, **kwargs):

    if self is None: return False

    if self.weekday() > 4:
        return True
    else:
        return False

#Método para Adicionar Matriz. Essa página não é igual as outras, pois o Form não permite Update, somente Create.
#Essa diferença ocorre porque ao Inserir criamos uma matriz com um Intervalo de Dias para uma única Escala de Serviço, Mas
#Ao alterar a Matriz alteramos Várias Escalas de Serviço em um Único Dia. (IMPORTANTE)
def matrizAdd(request):

    '''
    Ao Alterarmos uma Matriz, devemos limpar os serviços para recalcular tudo novamente
    '''
    
    PageTitle = 'Add Matriz SV'


    if request.method == 'POST':

        form = MatrizAddForm(request.POST, request.FILES)

        if form.is_valid():
            DateBegin = form.cleaned_data['DtBegin_Matriz']
            DateEnd = form.cleaned_data['DtEnd_Matriz']
            Id_SubTipEsc = form.cleaned_data['Id_SubTipEsc']
            NumMil_Matriz = form.cleaned_data['NumMil_Matriz']

            while DateBegin <= DateEnd:
                MatrizSearchObject = Matriz.objects.filter(Id_SubTipEsc=Id_SubTipEsc, Dt_Matriz = DateBegin)
  
                if  MatrizSearchObject.count() == 0:
                    Matriz.objects.create(
                            Id_SubTipEsc = Id_SubTipEsc,
                            Dt_Matriz = DateBegin,
                            NumMil_Matriz = NumMil_Matriz,
                            IsHolyday_Matriz = IsHolyday(DateBegin)
                        )
                
                DateBegin = DateBegin + timedelta(days=1)   

            servicoDel(DateBegin=DateBegin) #Exclui todos os serviços apartir de uma data

            return HttpResponseRedirect(reverse('matriz'))
    else:
        form = MatrizAddForm()

    context = {          
        'form':form,
        'PageTitle': PageTitle
    } 

    return render(request, "PJI110/matrizAdd.html", context)   

#Método para Excluir Matriz.
def matrizDel(request):

    '''
    Igual ao Método de Add ao excluirmos dados de uma Matriz, devemos limpar os serviços para recalcular tudo novamente
    '''

    PageTitle = 'Del Matriz SV'

    if request.method == 'POST':

        form = MatrizDelForm(request.POST, request.FILES)

        if form.is_valid():
            DateBegin = form.cleaned_data['DtBegin_Matriz']
            DateEnd = form.cleaned_data['DtEnd_Matriz']
            Id_SubTipEsc = form.cleaned_data['Id_SubTipEsc']

            while DateBegin <= DateEnd:
                MatrizSearchObject = Matriz.objects.filter(Id_SubTipEsc=Id_SubTipEsc, Dt_Matriz = DateBegin)

                if MatrizSearchObject.count() != 0:
                    for MatrizSearchItem in MatrizSearchObject:
                        MatrizSearchItem.delete()
                        
                
                DateBegin = DateBegin + timedelta(days=1)   
            
            servicoDel(DateBegin=DateBegin) #Exclui todos os serviços apartir de uma data

            return HttpResponseRedirect(reverse('matriz'))
    else:
        form = MatrizDelForm()

    context = {          
        'form':form,
        'PageTitle': PageTitle
    } 

    return render(request, "PJI110/matrizDel.html", context)     

#Método para Excluir Matriz.
def matrizEdit(request):

    '''
    Igual ao Método de Add ao Editarmos dados de uma Matriz, devemos limpar os serviços para recalcular tudo novamente
    '''

    PageTitle = 'Editar Matriz SV'

    if request.method == 'POST':

        form = MatrizEditForm(request.POST, request.FILES)

        if form.is_valid():
            DateBegin = form.cleaned_data['DtBegin_Matriz']
            DateEnd = form.cleaned_data['DtEnd_Matriz']
            IsHolyday = form.cleaned_data['IsHolyday_Matriz']

            while DateBegin <= DateEnd:
                MatrizSearchObject = Matriz.objects.filter(Dt_Matriz = DateBegin)

                if MatrizSearchObject.count() != 0:
                    for MatrizSearchItem in MatrizSearchObject:
                        MatrizSearchItem.IsHolyday_Matriz = IsHolyday
                        MatrizSearchItem.save()
                
                DateBegin = DateBegin + timedelta(days=1)   

            servicoDel(DateBegin=DateBegin) #Exclui todos os serviços apartir de uma data

            return HttpResponseRedirect(reverse('matriz'))
    else:
        form = MatrizEditForm()

    context = {          
        'form':form,
        'PageTitle': PageTitle
    } 

    return render(request, "PJI110/matrizEdit.html", context)      

#Método para Adicionar Mês. É importante para criar filtros de Pesquisa com intervalos de 30 dias
def addMonths(dt, months = 0):
    new_month = months + dt.month
    year_inc = 0
    if new_month>12:
        year_inc +=1
        new_month -=12
    return dt.replace(month = new_month, year = dt.year+year_inc)

#Método Principal para Exibir a Matriz na Página
def matriz(request):

    PageTitle = 'Matriz SV'
    MonthOfSearch = ''
    TipEscOfMatriz = ''
    SelectOfMatriz = ''
    SubTipoEscalaList = ''

    if len(request.GET) > 0:
        for action in request.GET:
            if action == "MatrizSearch":
                MonthOfSearch = int(request.GET['DateOfMatriz'])
                TipEscOfMatriz = int(request.GET['TipoEscalaOfMatriz'])
                SelectOfMatriz = MatrizSelectForm(request.POST or None, instance={'DateOfMatriz':MonthOfSearch, 'TipoEscalaOfMatriz': TipEscOfMatriz})
            else:
                if action == "MatrizAdd":
                    return matrizAdd(request)
                else:
                    if action == "MatrizDel":
                        return matrizDel(request)
                    else:
                        if action == "MatrizEdit":
                            return matrizEdit(request)
    else:
        MonthOfSearch = datetime.now().month
        TipEscOfMatriz = 0
        SelectOfMatriz = MatrizSelectForm()
        
    DateBegin = datetime(datetime.now().year, MonthOfSearch, 1)
    DateEnd =  addMonths(DateBegin, 1)
    
    MatrizList = Matriz.objects.filter(Dt_Matriz__range=[DateBegin, DateEnd], Id_SubTipEsc__Id_TipEsc_id = TipEscOfMatriz).order_by('Dt_Matriz', 'Id_SubTipEsc')

    SubTipoEscalaList = Matriz.objects.values('Id_SubTipEsc__Nome_SubTipEsc').filter(Id_SubTipEsc__Id_TipEsc_id = TipEscOfMatriz).order_by('Id_SubTipEsc').distinct()

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
                        ListEscala.append([ItemOfMatriz.NumMil_Matriz, ItemOfMatriz.IsHolyday_Matriz])    
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
        'MonthOfMatriz':SelectOfMatriz,
        
    } 

    return render(request, "PJI110/matriz.html", context, )  

#Novamente devemos formatar os Dados antes de Passar para o Context, porque o Django não permite trabalhar com os dados no Template
#Se fosse em uma linguagem mais robusta poderíamos fazer essa lógica específica de visualização e formatação dos dados no próprio código HTML.
def FormatListServico(ListServico, SubTipoEscalaList):
    ListTempplate = list()
    
    #Seleciona Todos os Dias Que existem Sv
    for ItemListServico in ListServico: 
        ListTemporary = list()                           

        #Para Cada Dia devemos verificar se existe todos os SubTipoEscala
        for ItemSubtipEsc in SubTipoEscalaList:
            flag = False
            for ItemSvSubTipEsc in ItemListServico[1]: #Caso encontre o SubTipoEscala no Dia Adicionamos os Dados e podemos executar um Break
                if ItemSvSubTipEsc[0] ==  ItemSubtipEsc.id:
                    flag = True
                    ListTemporary.append([ItemSvSubTipEsc[0], ItemSvSubTipEsc[1], ItemSvSubTipEsc[2],ItemSvSubTipEsc[3]])
                    break
            if flag: 
                flag = False
            else:    
                ListTemporary.append([ItemSubtipEsc.id,False, 0,[[' ', '---', ' ']]]) #Insira Strings Vazias para não ter erros Futuros na Execução
        ListTempplate.append([ItemListServico[0], ListTemporary])    
    return ListTempplate
 

#Método para Adicionar o Militar no Serviço
def AppendMilitarIntoServico(ListMilitarDispensado, ListMilitaresServico, ListServico, ListTemp, ItemMatrizEscala):
    
    '''
    Para Adicionar o Militar no Serviço Devemos Realizar as seguintes Validções
    '''
    '''
    Verificar se O Militar Está dispensa nesse dia de Serviço
    '''
    '''
    Verificar Se o Militar Não foi adicionado no Model Serviço 48h antes ou 48 Depois Em outro TipoEscala.
    Os Inserts dos Militares é Feito pela Prioridade da Escala de Serviço
    '''
    '''
    Verificar Se o Militar não foi Adicionado no Model Serviço 48h antes no mesmo TipoEscala 
    (Nesse Caso O Model não foi Salvo, mas apenas gerado por vetores, como é o caso da Escala PRETA e VERMELHA).
    '''

    #Indice Começa em 0, porque é o Primeiro Militar da Lista é o próximo a ser escalado
    xV = 0
    LenListMilitaresServico = len(ListMilitaresServico)
    if(LenListMilitaresServico > 0):
        #Condição para não Adicionar o Militar que Esta Dispensado nesse Dia
        while(ListMilitarDispensado.filter(Id_Mil = ListMilitaresServico[xV].id).count() >0):
            #Se o militar não pode ser Escalado, então pegamos o Próximo da Lista Disponível
            if(LenListMilitaresServico < (xV + 1)):
                xV = xV + 1
            else:
                xV = 0    

        #Condição para Verificar se o Militar Ja Está de Serviço em Outro Tipo de Servço
        #A Condição Deverá Vericar 2 Dias Antes e 2 Dias Depois. Pois 48h é o Intervalo Mínimo entre 1 Serviço e Outro
        DtBegin = ItemMatrizEscala.Dt_Matriz - timedelta(days=2)
        DtEnd = ItemMatrizEscala.Dt_Matriz
        while(Servico.objects.filter(Id_Matriz__Dt_Matriz__range=[DtBegin,DtEnd], Id_Mil = ListMilitaresServico[xV].Id_Mil).count() > 0):
            if(LenListMilitaresServico < (xV + 1)):
                xV = xV + 1
            else:
                xV = 0 

        #Condição para Verificar se o Militar Já Está de Serviço Na Escala Preta
        #A Condição Deverá Verificar 2 dias Antes. Pois o Intervalo Mínimo de 1 Serviço para Outro é também de 48h
        NumListSV = len(ListServico)
        y = NumListSV - 2
        
        if(y < 0):
            y=0
        
        reset = False #Inicialização de variável
        
        while(y < NumListSV):
            for ItemTipSv in ListServico[y][1]:
                for Item in ItemTipSv[3]:    
                    #Caso o Militar Esteja nesses 2 dias pegamos o Próximo Militar da Escala 
                    while(Item[1] == ListMilitaresServico[xV].Id_Mil):
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
        ListTemp.append([ListMilitaresServico[xV].Id_Mil.Id_PG.Nome_PG, ListMilitaresServico[xV].Id_Mil, ListMilitaresServico[xV].Id_Mil.Id_SU.Nome_SU]) 

        #Retiramos o Militar Escalado e Colocamos no final da Fila, pois ele passa a ser o Mais folgado na Escala de Serviço  
        ListMilitaresServico.append(ListMilitaresServico[xV]) 
        ListMilitaresServico.pop(xV)


#Método Para Construir a Escala de Serviço. Esse Método está muito grande, então separei em uma função
def BiuldServico(DateBegin, DateEnd, Id_TipEscForm, SubTipoEscalaList, ListServico):
    
    #Pesquisar a Matriz de Acordo com o Filtro do Usuário
    MatrizEscala =  Matriz.objects.filter(Dt_Matriz__range=[DateBegin, DateEnd], Id_SubTipEsc__Id_TipEsc = Id_TipEscForm)
    if(len(MatrizEscala) > 0):

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

        ListTempDia = list()
        LastListMatrizEscala = ListMatrizEscala[len(ListMatrizEscala)-1] #Ultimo Elemento da Matriz
        IndexMatrizEscala = 0
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

            ListTempDia.append([ItemMatrizEscala.Id_SubTipEsc.id, ItemMatrizEscala.IsHolyday_Matriz, ItemMatrizEscala,ListTemp])

            #Adiciona Todos Os Serviços do SubTipo da Escala Concatenados em Vetores. (Esse Concatenação é importante, pois será usado na iteração For-For)
            if(ItemMatrizEscala == LastListMatrizEscala or ItemMatrizEscala.Dt_Matriz != ListMatrizEscala[IndexMatrizEscala + 1].Dt_Matriz):    
                ListServico.append([ItemMatrizEscala.Dt_Matriz, ListTempDia])  
                ListTempDia = list()

            IndexMatrizEscala = IndexMatrizEscala + 1 

    #Formata os Dados Para Tabela em HTML. TEM que fazer isso no VIEW, porque o DJANGO não permite criar sequer uma FLAG no Template.
    #Em qualquer outra linguagem isso não seria nessário e também seria muito mais fácil de trabalhar os dados no TEMPLATE    
    return FormatListServico(ListServico, SubTipoEscalaList) 

def homeAdd(request, *args, **kwargs):

    # CreateMilitarDatabase()

    PageTitle = 'Gerar Escala de SV 1º B Av Ex'
    SubTipoEscalaList = list()
    #Essa Lista Será Exibida na Página e Após ser Homologada Será Salva na Base de Dados
    ListServico = list()
    ListServicoTemplate = list()
    
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

            ListServicoTemplate = BiuldServico(DateBegin, DateEnd, Id_TipEscForm, SubTipoEscalaList, ListServico)    

            if 'ServicoAdd' in request.POST:
                #Comit na Base de Dados Para Adicionar o Serviço
                if(len(ListServico) > 0):        
                    for ItemListServico in ListServico:
                        for Item in  ItemListServico[1]:
                            for ItenMil in  Item[3]:
                                if(Servico.objects.filter(Id_Matriz = Item[2], Id_Mil = ItenMil[1].id).count() == 0):
                                    Servico.objects.create(Id_Matriz = Item[2], Id_Mil = ItenMil[1])
                
                return HttpResponseRedirect('./')

    else:
        form = ServicoForm()

        #Recupera o Primerio Tipo Escala para inserir no FORM.
        filtroTipoEscala = TipoEscala.objects.all()[:1][0]
        ServicoList = Servico.objects.filter(Id_Matriz__Id_SubTipEsc__Id_TipEsc = filtroTipoEscala).order_by('-Id_Matriz__Dt_Matriz')[:5]

    context = {  
        'ListServicoTemplate':ListServicoTemplate,
        'PageTitle':PageTitle,
        'SubTipoEscalaList': SubTipoEscalaList,
        'form':form,        
    } 

    return render(request, "PJI110/homeAdd.html", context) 

def Home(request, *args, **kwargs):

    PageTitle = 'Escala de SV 1º B Av Ex'
    SubTipoEscalaList = list()
    ListServicoTemplate = list()
    ListServicoTemp = list()
    DateBegin = timezone.now()
    DateEnd = timezone.now()
    Id_TipEscForm = TipoEscala.objects.all()[:1][0]

    if request.method == 'POST':
        
        if "ServicoAdd" in request.POST: return HttpResponseRedirect('homeAdd')

        form = ServicoForm(request.POST, request.FILES)

        if form.is_valid():
            DateBegin = form.cleaned_data['DtBegin_Servico']
            DateEnd = form.cleaned_data['DtEnd_Servico']
            Id_TipEscForm = form.cleaned_data['Id_TipEsc']
    else:
        form = ServicoForm()
    
    #Atualiza a Caixa de Pesquisa de Acordo com o Filtro do Usuário
    SubTipoEscalaList  = SubTipoEscala.objects.filter(Id_TipEsc = Id_TipEscForm)  

    #Recupera todos os Serviços no Período Selecionado
    ListServico = Servico.objects.filter(Id_Matriz__Dt_Matriz__range=[DateBegin, DateEnd], Id_Matriz__Id_SubTipEsc__Id_TipEsc = Id_TipEscForm)

    if(len(ListServico)):
        
        ListSubTipEscTemp = list()

        #Incialização das Variáveis
        x = -1
        IMatriz = ListServico[0].Id_Matriz
        ISubTipEsc = ""

        #Inicia a Varredura em Todos os Itens da Pesquisa
        for ItemServico in ListServico:
            
            #Adiciona Todos os Tipo de Serviços na mesma Data
            if(IMatriz.Dt_Matriz != ItemServico.Id_Matriz.Dt_Matriz):
                
                ListServicoTemp.append([IMatriz.Dt_Matriz, ListSubTipEscTemp]) #Comando para Adicionar a Data com as Informações
                
                #Limpa os Tipo de Serviços para o Próximo Dia
                ListSubTipEscTemp = list()
                ISubTipEsc = ""
                x = -1

                #Atualiza a nova Data na Variável de Comparação
                IMatriz = ItemServico.Id_Matriz
               
            #Condição para Agrupar Todos Os Militares no mesmo SubTipoServiço 
            if(ISubTipEsc != ItemServico.Id_Matriz.Id_SubTipEsc):
                ISubTipEsc = ItemServico.Id_Matriz.Id_SubTipEsc  
                ListSubTipEscTemp.append([ISubTipEsc, ItemServico.Id_Matriz, []]) #O Colchetes (Posição 2) é para inserir os Militares Futuramente
                x = x + 1                

            #A Lista de Militares é a Ultima Posição (2) do Vetor ListSubTipEscTemp
            ListSubTipEscTemp[x][2].append(ItemServico.Id_Mil)   

        ListServicoTemp.append([IMatriz.Dt_Matriz, ListSubTipEscTemp])

        
        xIndex = 0
        
        #O Django não permite criar Flag no Template, Logo se existir Algum SubTipoServiço que esteja Vazio temos que Iserir uma Informação "0"
        #Para Isso Temos que Comparar a Matriz de Serviço com todos os SubTipoServiço e quando não existir na MatrizServiço Adicionamos o "0"
        for Dias in ListServicoTemp:
            
            ListServicoTemplate.append([Dias[0], []])

            #Recupera e Itera Todos os SubTipoServiço
            for TiposEscala in SubTipoEscalaList:
                Flag = False
                y = 0

                #Condição para Verificar se Esse SubTipoServiço existe no Dia
                for ItemTipoEscala in Dias[1]:
                    if(ItemTipoEscala[0] == TiposEscala): 
                        Flag = True
                        break
                    y = y + 1

                if Flag:
                    ListServicoTemplate[xIndex][1].append([Dias[1][y][0], Dias[1][y][1], Dias[1][y][2]])
                    Flag = False
                else:
                    ListServicoTemplate[xIndex][1].append([TiposEscala, 0,['---']])    
            xIndex = xIndex + 1



    context = {  
        'ListServicoTemplate':ListServicoTemplate,
        'PageTitle':PageTitle,
        'SubTipoEscalaList': SubTipoEscalaList,
        'form':form,        
    }

    return render(request, "PJI110/home.html", context) 