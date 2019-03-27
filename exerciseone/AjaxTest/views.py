from django.shortcuts import render
import os

# Create your views here.
def test(request):
    print(os.getcwd())
    return render(request, 'AjaxTest/react_test.html')

def test1(request):
    return render(request, 'AjaxTest/react_test1.html')
