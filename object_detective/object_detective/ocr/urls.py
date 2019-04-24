from django.urls import path

from ocr import views

urlpatterns = [
    path('', views.index, name="index"),
    path('upload/', views.upload_image, name='upload'),
    path('image/<int:id>/', views.original_image, name='original_image'),
    path('image/', views.image, name='image'),
    path('history/', views.history, name='history'),
    path('favorite/', views.favorite, name="favorite"),
    path('add_to_favorite/<int:id>/', views.add_to_favorite, name='add_to_favorite'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]