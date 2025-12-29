from django.urls import path
from mainapp.views import views

urlpatterns = [
    path("", views.index, name="index"),
]