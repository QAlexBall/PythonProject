from django.shortcuts import render
import os

# Create your views here.
def test(request):
    print(os.getcwd())
    return render(request, 'AjaxTest/test1.html')