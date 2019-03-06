
from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('write/', views.write_article, name='write'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('<int:article_id>/comment/', views.write_comment, name='write_comment'),
    # path('<int:article_id>/', views.ArticleAndCommentView.as_view(), name='article_content')
    path('<int:article_id>/', views.article_content, name='article_content'),
    path('<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('<int:article_id>/delete/', views.del_article, name='del_article'),
]