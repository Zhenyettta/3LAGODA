from django.http import HttpResponse, HttpResponseRedirect
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
                    return redirect_to_manager_page()
                else:
                    return redirect_to_home_page()

    return HttpResponse(status=204)


def extract_form_data(form):
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    return email, password


def authenticate_user(email, password):
    password = password.encode('utf-8')
    with connection.cursor() as cursor:
        cursor.execute("SELECT email, password, role FROM employee")
        logins = cursor.fetchall()
        for elem in logins:
            if elem[0] == email and bcrypt.checkpw(password, elem[1].tobytes()):
                user.email = email
                user.password = password
                user.role = elem[2]
                return True
        return False


def home_page(request):
    if not user_is_manager():
        return render(request, 'home.html')
    return HttpResponse(status=204)


def manager_page(request):
    if user_is_manager():
        return render(request, 'manager.html')
    return HttpResponse(status=204)


def redirect_to_home_page():
    if not user_is_manager():
        return HttpResponseRedirect('/home')
    return HttpResponse(status=204)


def redirect_to_manager_page():
    if user_is_manager():
        return HttpResponseRedirect('/manager')
    return HttpResponse(status=204)


def user_is_manager():
    return user.role == 'Manager'


def encryption():
    password = "123"
    password = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
    print(bcrypt.checkpw(password, hashedPassword))
    print(hashedPassword)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE employee SET password = %s WHERE employee_id = %s", (hashedPassword, 2))


def empl_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM employee WHERE role = 'Sales'")
        employees = cursor.fetchall()

    return render(request, 'empl_list.html', {'employees': employees})
