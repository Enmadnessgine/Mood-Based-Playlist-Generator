from django.urls import path
from mainapp.views.views import dashboard, index

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
]