from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


# Create your models here.
class Article(models.Model):
    article_id = models.AutoField('article id', primary_key=True, unique=True)
    article_title = models.CharField('article title', max_length=20, unique=True)
    article_context = models.TextField('article context')
    article_created_time = models.DateTimeField('article created time', auto_now=True)

    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.article_created_time <= now

    def __str__(self):
        return self.article_title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment_context = models.TextField('comment context')
    comment_create_time = models.DateTimeField('comment created time', auto_now=True)

    def __str__(self):
        return self.comment_context

class ImageAlbum(models.Model):

    album_user = models.ForeignKey(User, on_delete=models.CASCADE)
    album_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    album_img = models.ImageField(upload_to='upload')
