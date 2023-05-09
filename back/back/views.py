from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from .forms import LoginForm
import bcrypt

def show_form(request):
    form = LoginForm()
    return render(request, 'login.html', {"form": form})


def submit_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            encryption()
            if my_custom_sql(email, password):
                with connection.cursor() as cursor:
                    cursor.execute("SELECT role FROM employee WHERE email = %s", [email])
                    role = cursor.fetchone()
                    print(type(role))
                    if role[0] == 'Manager':
                        return manager_page(request)
                    else:
                        return home_page(request)
    return HttpResponse(status=204)

def my_custom_sql(email, password):
    with connection.cursor() as cursor:
        cursor.execute("SELECT email, password, role FROM employee")
        logins = cursor.fetchall()
        for elem in logins:
            if elem[0] == email and elem[1] == password:
                return True
        return False


def home_page(request):
    return render(request, 'home.html')

def manager_page(request):
    return render(request, 'manager.html')

def encryption():
    password = "abvsdaf123абобус"
    password = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
    print(bcrypt.checkpw(password, hashedPassword))
    print(hashedPassword)
