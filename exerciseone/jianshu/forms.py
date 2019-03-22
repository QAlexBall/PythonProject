# encoding: utf-8

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Comment, Article

class ArticleModelForm(ModelForm):

    class Meta:
        model = Article
        fields = ['title',
                  'context',
                  'image', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),            
            'context': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
        }

class CommentModelForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['context']
        
        widgets = {
            'context': forms.Textarea(attrs={'class': 'form-control', 
                                             'rows': 2,
                                             'id': 'comment_id'}),
        }

