# encoding: utf-8

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Article, Comment, ImageAlbum
from .forms import CommentModelForm, ArticleModelForm, ImageAlbumModelForm
import os
# Create your views here.


def index(request):
    list = []
    message = {}
    latest_article_list = None

    try:
        latest_article_list = Article.objects.order_by('-article_created_time')
    except Article.DoesNotExist:
        message["article_not_exist"] = "文章不存在!"

    for article in latest_article_list:
        try:
            album = ImageAlbum()
            album = ImageAlbum.objects.get(album_article=article)
        except ImageAlbum.DoesNotExist:
            error_message = "image for " + str(article.article_title) + " does not exist"
            message["error_message"] = error_message
            print(error_message)
        list.append((article, album))

    message['list'] = list
    return render(request, 'jianshu/index.html', message)

@csrf_exempt
@login_required(login_url='login')
def write_article(request):
    message = {}

    if request.method == "POST":
        article_form = ArticleModelForm(request.POST)
        img = request.FILES.get('img')
        if img is None:
            return HttpResponse("图片加载失败")
        elif article_form.is_valid():
            article_form.save()
            # ImageAlbumModelForm不知道如何用
            article = Article.objects.get(article_title=request.POST.get('article_title'))
            try:
                img = ImageAlbum(album_user=request.user,
                                 album_article=article,
                                 album_img=img)
                img.save()
            except:
                message["img_error"] = "图片保存失败"
        else:
            return HttpResponse("文章缺少标题或内容")
        return redirect('index')

    message["created_time"] = timezone.now()
    return render(request, 'jianshu/write.html', message)


@csrf_exempt
def article_content(request, article_id):
    message = {}
    album = ImageAlbum()
    article = Article.objects.get(article_id=article_id)
    comments = Comment.objects.filter(article=article).order_by('-comment_create_time')[:5]
    try:
        album = ImageAlbum.objects.get(album_article=article)
    except ImageAlbum.DoesNotExist:
        message["img_error"] = "图片不存在"

    if album.album_user.username == request.user.username:
        message['edit_and_delete'] = True

    message['article'] = article
    message['comments'] = comments
    message['album'] = album
    message['user_name'] = album.album_user.username

    return render(request, 'jianshu/article_content.html', message)

@csrf_exempt
@login_required(login_url='login')
def edit_article(request, article_id):
    message = {}
    article = Article.objects.get(article_id=article_id)


    if request.method == "POST":
        context = request.POST['context']
        Article.objects.filter(article_id=article_id).update(article_context=context)
        return redirect('article_content', article_id=article_id)

    message["article"] = article

    return render(request, 'jianshu/edit.html', message)

@csrf_exempt
def del_article(request, article_id):
    if request.method == 'GET':
        return render(request, 'jianshu/delete_article.html')
    else:
        confirm_info = request.POST['confirm']
        if confirm_info == 'y':
            article = Article.objects.filter(article_id=article_id).first()
            album = ImageAlbum.objects.filter(album_article=article).first()
            path = album.album_img
            img_path = str(os.getcwd()) + '/jianshu/static/media/' + str(path)
            os.remove(img_path)
            album.delete()
            article.delete()
            return redirect('index')
        else:
            return redirect('article_content', article_id=article_id)

@csrf_exempt
@login_required(login_url='login')
def write_comment(request, article_id):
    message = {}
    article = Article()
    try:
        article = Article.objects.get(article_id=article_id)
    except Article.DoesNotExist:
        error_message = "Article id " + str(article_id) + "does not exist !"
        message["error_message"] = error_message
        print(error_message)

    if request.method == "POST":
        message = {"status": "failed", "message": "添加失败"}
        comment_form = CommentModelForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()
            message["status"] = "success"
            message["message"] = "添加成功"
        return JsonResponse(message)

    comments = Comment.objects.filter(article=article).order_by("-comment_create_time")
    message["article"] = article
    message["comments"] = comments
    return render(request, "jianshu/write_comment.html", message)

@csrf_exempt
def register(request):
    message = {}

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            message["error_info"] = "请输入完整的注册信息"
        else:
            if User.objects.filter(username=username) or User.objects.filter(email=email):
                message["user_exist"] = "用户名或邮箱已经存在!"
            elif password1 != password2:
                message["password_not_same"] = "两次密码不同!"
            else:
                user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password1)
                user.save()
                user_login = authenticate(request, username=username, email=email, password=password1)
                login(request, user_login)
                return redirect('index')

    return render(request, 'jianshu/register.html', message)

@csrf_exempt
def user_login(request):
    message = {}

    if request.method == "POST":
        if not request.POST.get('username'):
            message["no_username"] = "用户名为空"
        elif not request.POST.get('password'):
            message["no_password"] = "密码为空"
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                message["error"] = "用户名或密码错误"

    return render(request, 'jianshu/login.html', message)

def user_logout(request):
    logout(request)
    return redirect('index')

