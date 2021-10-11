from django.db.models import query
from django.urls import path
from PJI110 import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from PJI110.models import SU
from PJI110.models import PostGrad
from PJI110.models import Militar

'''
militar_list_view = views.MilitarListView.as_view(
    queryset = Militar.objects.select_related("Id_SU", "Id_PG"),
    context_object_name = "militarList",
    template_name="PJI110/militares.html"
)'''

urlpatterns = [
    path("", views.Home, name="home"),
    path("escala/", views.escala, name="escala"),
    path("militares/", views.getdata, name="militares"),
    path("matriz/", views.matriz, name="matriz"),
    path("dispensa/", views.dispensa, name="dispensa"),
    path("militarAdd/<id>", views.militarAdd, name="militarAdd"),
    path("militarHidden/", views.militarAdd, name="militarHidden"),
    ]

urlpatterns += staticfiles_urlpatterns()
