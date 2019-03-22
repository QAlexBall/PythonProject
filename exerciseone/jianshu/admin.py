from django.contrib import admin

# Register your models here.

from .models import Article, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 5

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_time')
    fieldsets = [
        ('Title',            {'fields': ['title']}),
        ('Context',          {'fields': ['context']})
    ]
    inlines = [CommentInline]
    list_filter = ['created_time']
    search_fields = ['title']

admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment)
