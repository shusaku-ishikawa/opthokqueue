# chat/urls.py
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'main'

urlpatterns = [
    path('', views.Login.as_view(), name = "login"),
    path('logout', views.Logout.as_view(), name = "logout"),
    path('userentry', views.UserEntryView.as_view(), name = 'userentry'),
    path('clinicadmin', views.ClinicAdminView.as_view(), name = 'clinicadmin'),
    path('listuserentry', views.ListUserEntryView.as_view(), name = 'listuserentry'),   
]