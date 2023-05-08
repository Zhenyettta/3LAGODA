from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from .forms import LoginForm


def show_form(request):
    form = LoginForm()
    return render(request, 'login.html', {"form": form})


def submit_form(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if my_custom_sql(email, password):
            return home_page(request)
        else:
            error_message = "Invalid password. Please try again."
            return render(request, 'login.html', {"form": LoginForm(), "error_message": error_message})


def my_custom_sql(email, password):
    with connection.cursor() as cursor:
        cursor.execute("SELECT email, password FROM employee")
        logins = cursor.fetchall()
        for elem in logins:
            if elem[0] == email and elem[1] == password:
                return True
        return False

def home_page(request):
    return render(request, 'home.html')