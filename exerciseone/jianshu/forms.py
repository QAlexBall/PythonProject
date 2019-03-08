# encoding: utf-8

from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Comment, Article, ImageAlbum

class CommentModelForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['article',
                  'comment_context',]

class ArticleModelForm(ModelForm):

    class Meta:
        model = Article
        fields = ['article_title',
                  'article_context',]

class ArticleContextModelForm(ModelForm):

    class Meta:
        model = Article
        fields = ['article_context']

class UserModelForm(ModelForm):

    class Meta:
        model = User
        fields = ['username',
                  'password', ]

class ImageAlbumModelForm(ModelForm):

    class Meta:
        model = ImageAlbum
        fields = ['album_img']