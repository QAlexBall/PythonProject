from django.shortcuts import render, redirect, get_list_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Article, User, Comment, Album
from django.template import loader
from django.http import HttpResponse
from django.utils import timezone
import os
# Create your views here.

def index(request):
    result = []
    latest_article_list = Article.objects.order_by('article_created_time')
    for article in latest_article_list:
        album = Album.objects.filter(album_article=article).first()
        result.append((article, album))
    info = {
        'info_list': result,
    }
    return render(request, 'jianshu/index.html', info)

@csrf_exempt
def write_article(request):
    user_name = request.COOKIES.get('user_name')
    if user_name == None:
        return redirect('login')
    info = {
        'user_name': user_name,
        'created_time': timezone.now(),
    }
    if request.method == 'GET':
        templates = loader.get_template('jianshu/write.html')
        return HttpResponse(templates.render(info, request))
    else:
        img = request.FILES.get('img')
        print(img)
        if not img:
            return HttpResponse('image load error!')

        user = User.objects.filter(user_name=user_name).first()
        article_title = request.POST['title']
        article_context = request.POST['context']
        if Article.objects.filter(article_title=article_title).filter():
            return HttpResponse('article exist!')
        else:
            Article.objects.create(article_title=article_title,
                                   article_context=article_context,
                                   article_created_time=info['created_time'])
            article = Article.objects.filter(article_title=article_title).first()
            image = Album(
                album_user=user,
                album_article=article,
                album_img=img,
            )
            image.save()
            return redirect('index')

@csrf_exempt
def article_content(request, article_id):
    templates = loader.get_template('jianshu/article_content.html')
    article = Article.objects.filter(article_id=article_id).first()
    album = Album.objects.filter(album_article=article).first()
    comments = Comment.objects.order_by('-comment_create_time', )

    # 获取该文章的评论
    article_comments = []
    for comment in comments:
        if comment.article.article_id == article_id:
            article_comments.append(comment)
        else:
            pass

    info = {
        'article_id': article.article_id,
        'article_title': article.article_title,
        'article_context': article.article_context,
        'article_created_time': article.article_created_time,
        'album_img': album.album_img,
        'user_name': album.album_user.user_name,
        'comments': article_comments[:5],
        'comment_created_time': timezone.now(),
        'edit_and_delete': False,
    }
    user_name = request.COOKIES.get('user_name')

    # 确认当前用户是否是该图片的作者 info['user_name']实际上是
    if user_name == info['user_name']:
        info['edit_and_delete'] = True

    # 提交评论
    if request.method == 'POST':
        comment_context = request.POST['comment']

        # 评论不能为空未登录无法评论
        if not comment_context or not user_name:
            return redirect('article_content', article_id=article_id)

        Comment.objects.create(article_id=info['article_id'],
                               comment_context=comment_context,
                               comment_create_time=info['comment_created_time'])
        comments = Comment.objects.order_by('comment_create_time')
        article_comments = []
        for comment in comments:
            if comment.article.article_id == article_id:
                article_comments.append(comment)
            else:
                pass
        info['comments'] = article_comments[:5]
        return render(request, 'jianshu/article_content.html', info)
    return HttpResponse(templates.render(info, request))

@csrf_exempt
def write_comment(request, article_id):
    comments = Comment.objects.order_by('comment_create_time')
    article_comments = []
    for comment in comments:
        if comment.article.article_id == article_id:
            article_comments.append(comment)
        else:
            pass
    info = {
        'article_id': article_id,
        'comments' : article_comments,
    }
    # POST
    if request.method == 'POST':
        print('POST')
        comments = request.POST.get('article_comments')
        if comments != "":
            comment = Comment()
            comment.article_id = article_id
            comment.comment_context = comments
            comment.comment_create_time = timezone.now()
            comment.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')
    return render(request, 'jianshu/write_comment.html', info)


@csrf_exempt
def edit_article(request, article_id):
    article = Article.objects.filter(article_id=article_id).first()
    article_info = {
        'title': article.article_title,
        'context': article.article_context,
    }
    if request.method == 'GET':
        return render(request, 'jianshu/edit.html', article_info)
    else:
        # title = request.POST['title']
        context = request.POST['context']
        # 跟新文章
        Article.objects.filter(article_id=article_id).update(article_context=context)
        return redirect('article_content', article_id=article_id)

@csrf_exempt
def del_article(request, article_id):
    if request.method == 'GET':
        return render(request, 'jianshu/delete_article.html')
    else:
        confirm_info = request.POST['confirm']
        if confirm_info == 'y':
            article = Article.objects.filter(article_id=article_id).first()
            album = Album.objects.filter(album_article=article).first()
            path = album.album_img
            img_path = str(os.getcwd()) + '/jianshu/static/media/' + str(path)
            os.remove(img_path)
            album.delete()
            article.delete()
            return redirect('index')
        else:
            return redirect('article_content', article_id=article_id)

@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'jianshu/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.filter(user_name=username, user_password=password).first()
        if user:
            response = redirect("index")
            response.set_cookie("user_name", user.user_name, 604800)
            return response
        else:
            return render(request,
                          'jianshu/login.html',
                          {'error' : 'username or password error!'})

def logout(request):
    response = redirect('login')
    response.delete_cookie("user_name")
    return response

@csrf_exempt
def register(request):
    if request.method == 'GET':
        return render(request, 'jianshu/register.html')
    else:
        username = request.POST['username']
        telephone = request.POST['telephone']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        user_tel = User.objects.filter(user_tel=telephone).first()
        user_name = User.objects.filter(user_name=username).first()
        if user_tel == None and user_name == None:
            if password1 != password2:
                return HttpResponse('please enter your password again.')
            else:
                User.objects.create(user_name=username,
                                user_tel=telephone,
                                user_password=password2)
                return redirect("login")
        else:
            return render(request,
                          'jianshu/register.html',
                          {'error': 'register again!'})

