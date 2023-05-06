from django.http import HttpResponse
from django.shortcuts import render


def show_form(request):
    return render(request, 'login.html')


def submit_form(request):
    if request.method == 'POST':
        name = request.POST['name']
        if name == 'Viktor noob': return HttpResponse('100%')
        else:
            return HttpResponse('Ні!')
