from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from .forms import LoginForm
import bcrypt

from .user_data import User

user = User()

def show_form(request):
    form = LoginForm()
    return render(request, 'login.html', {"form": form})

def submit_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email, password = extract_form_data(form)
            if authenticate_user(email, password):
                print(repr(user))
                if user_is_manager():
                    return manager_page(request)
                else:
                    return home_page(request)

    return HttpResponse(status=204)

def extract_form_data(form):
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    return email, password

def authenticate_user(email, password):
    with connection.cursor() as cursor:
        cursor.execute("SELECT email, password, role FROM employee")
        logins = cursor.fetchall()
        for elem in logins:
            if elem[0] == email and elem[1] == password:
                user.email = email
                user.password = password
                user.role = elem[2]
                return True
        return False

def home_page(request):
    if not user_is_manager():
        return render(request, 'home.html')
    else:
        return HttpResponse(status=204)

def manager_page(request):
    if user_is_manager():
        return render(request, 'manager.html')
    else:
        return HttpResponse(status=204)

def user_is_manager():
    return user.role == 'Manager'

def encryption():
    password = "abvsdaf123абобус"
    password = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
    print(bcrypt.checkpw(password, hashedPassword))
    print(hashedPassword)
