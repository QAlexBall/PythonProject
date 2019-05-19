# encoding: utf-8

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core import serializers
import os

from .models import Article, Comment
from .forms import ArticleModelForm, CommentModelForm
import pytz
# Create your views here.

import markdown

def markdown_test(request, id):
    article = Article.objects.get(id=id)
    article.context = markdown.markdown(article.context, 
                                     extensions=[
                                     'markdown.extensions.extra',
                                     'markdown.extensions.codehilite',
                                     ])
    message = { 'article': article }
    if article.author == request.user:
            message["edit_and_delete"] = True
    return render(request, 'jianshu/markdown_test.html', message)

 

@csrf_exempt
def test(request):
    article_list = []

    latest_article_list = Article.objects.order_by("-created_time")[:30]

    fields = ['pk', 'title', 'context']
    for article in latest_article_list:
        article_dict = {}
        for field in fields:
            article_dict[field] = getattr(article, field)
        article_list.append(article_dict)

    return JsonResponse(article_list, safe=False)

def index(request):
    message = {}
    latest_article_list = None

    latest_article_list = Article.objects.order_by("-created_time")[:30]
    if latest_article_list.count() == 0:
        message["article_not_exist"] = "文章不存在!"

    message["article_list"] = latest_article_list
    return render(request, "jianshu/index.html", message)

@login_required(login_url="login")
def write_article(request):
    message = {}
    article_form = ArticleModelForm()

    if request.method == "POST":
        article_form = ArticleModelForm(request.POST, request.FILES)
        if article_form.is_valid():
            article_form_instance = article_form.save(commit=False)
            article_form_instance.author = request.user
            article_form_instance.save()
            return redirect("index")
        else:
            message["error_message"] = "article form error"
    
    message["form"] = article_form
    message["author"] = request.user    
    message["created_time"] = timezone.now()
    return render(request, "jianshu/write.html", message)

def article_content(request, id):
    message = {}
    article = Article()
    comment_form = CommentModelForm()
 
    try:
        article = Article.objects.get(id=id)
        if article.author == request.user:
            message["edit_and_delete"] = True
    except Article.DoesNotExist:
        message["article_not_exist"] = "当前文章不存在"
    
    if request.method == "POST":
        message = {"status": "failed", "message": "comment failed"}
        comment_form = CommentModelForm(request.POST)
        if comment_form.is_valid():
            comment_form_instance = comment_form.save(commit=False)
            comment_form_instance.article = article
            comment_form_instance.save()
            message["status"] = "success"
            message["message"] = "comment success"
            message["time"] = timezone.now()
        return JsonResponse(message)

    comments = Comment.objects.filter(article=article).order_by("-created_time")[:5]
    message["article"] = article
    message["comments"] = comments
    message["comment_form"] = comment_form
    return render(request, "jianshu/article_content.html", message)


@login_required(login_url="login")
def edit_article(request, id):
    message = {}
    article = Article()

    try:
        article = Article.objects.get(id=id)
    except Article.DoesNotExist:
        message["article_not_exist"] = "当前文章不存在"

    if article.author != request.user:
        message["permission_error"] = "PermissionError"
        return redirect("article_content")

    if request.method == "POST":
        if request.POST["article_context"]:
            Article.objects.filter(id=id).update(context=request.POST["article_context"])
            return redirect("article_content", id=id)
        else:
            return HttpResponse("文章修改失败")

    message["article"] = article
    return render(request, "jianshu/edit.html", message)

@login_required(login_url="login")
def del_article(request, id):
    message = {}
    article = Article()
    
    try:
        article = Article.objects.get(id=id)
    except Article.DoesNotExist:
        message["article_not_exist"] = "当前文章不存在"

    if article.author != request.user:    
        message["permission_error"] = "PermissionError"
        return redirect("article_content", id=id)
      
    if request.method == "POST":
        confirm_info = request.POST["confirm"]
        if confirm_info == "y":
            img_path = str(os.getcwd() + "/jianshu/static/media/" + str(article.image))
            os.remove(img_path)
            article.delete()
            return redirect("index")
        else:
            return redirect("article_content", id=id)

    return render(request, "jianshu/delete_article.html")

"""
    jsonResponse
    1.dict => json seclier =>string
    2.HttpResponse(string, mimeType="json/application")
"""

def register(request):
    message = {}

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

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
                return redirect("index")

    return render(request, "jianshu/register.html", message)

def user_login(request):
    message = {}

    if request.method == "POST":
        if not request.POST.get("username"):
            message["no_username"] = "用户名为空"
        elif not request.POST.get("password"):
            message["no_password"] = "密码为空"
        else:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                message["error"] = "用户名或密码错误"

    return render(request, "jianshu/login.html", message)

def user_logout(request):
    logout(request)
    return redirect("index")
