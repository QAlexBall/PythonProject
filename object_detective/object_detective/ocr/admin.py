from django.contrib import admin
from ocr.models import Image, Record, Favorite
# Register your models here.

admin.site.register(Image)
admin.site.register(Record)
admin.site.register(Favorite)