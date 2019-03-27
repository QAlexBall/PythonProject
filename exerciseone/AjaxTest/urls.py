
from django.urls import path

from . import views

urlpatterns = [
    path('/', views.test, name='test'),
    path('/1', views.test1, name='test1'),
]
