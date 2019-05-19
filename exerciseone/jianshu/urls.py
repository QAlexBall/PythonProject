
from django.urls import path

from . import views

urlpatterns = [
    path('markdown_test/<int:id>/', views.markdown_test, name='markdown_test'),   
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('write/', views.write_article, name='write'),
#    path('<int:id>/comment/', views.write_comment, name='write_comment'),
    path('<int:id>/', views.article_content, name='article_content'),

    path('<int:id>/edit/', views.edit_article, name='edit_article'),
    path('<int:id>/delete/', views.del_article, name='del_article'),
    path('test/', views.test, name='test')
]
