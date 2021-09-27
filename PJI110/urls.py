from django.urls import path
from PJI110 import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.Home, name="home"),
    path("escala/", views.escala, name="escala"),
    path("militares/", views.militares, name="militares"),
    path("matriz/", views.matriz, name="matriz"),
    path("dispensa/", views.dispensa, name="dispensa"),
    ]

urlpatterns += staticfiles_urlpatterns()
