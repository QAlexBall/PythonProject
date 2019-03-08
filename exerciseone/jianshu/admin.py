from django.contrib import admin

# Register your models here.

from .models import Article, Comment, ImageAlbum

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 5

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('article_id', 'article_title', 'article_created_time')
    fieldsets = [
        ('Title',            {'fields': ['article_title']}),
        ('Context',          {'fields': ['article_context']})
    ]
    inlines = [CommentInline]
    list_filter = ['article_created_time']
    search_fields = ['title']


# class AlbumInline(admin.TabularInline):
#     model = Album

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('user_id', 'user_name')
#     fieldsets = [
#         ('username', {'fields': ['user_name']}),
#     ]
#     inlines = [AlbumInline]

# admin.site.register(MyUser, UserAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
admin.site.register(ImageAlbum)