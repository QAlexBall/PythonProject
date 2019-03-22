from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


# Create your models here.
class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('article title', max_length=20, unique=True)
    context = models.TextField('article context')
    image = models.ImageField(upload_to='upload')
    created_time = models.DateTimeField('article created time', auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    context = models.TextField('comment context')
    created_time = models.DateTimeField('comment created time', auto_now=True)

    def __str__(self):
        return self.context

