from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import connection

from .forms import LoginForm, EmployeeForm
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


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_employee(
                data['surname'],
                data['name'],
                data['patronymic'],
                data['role'],
                data['salary'],
                data['date_of_birth'],
                data['date_of_start'],
                data['phone_number'],
                data['city'],
                data['zip_code'],
                data['email'],
                data['password']
            )
            return redirect('manager/employees/')
    else:
        form = EmployeeForm()
    return render(request, 'add_employee.html', {'form': form})


def delete_employee(request, id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM employee WHERE employee_id = %s", [id])
        cursor.execute("SELECT * FROM employee WHERE role = 'Sales'")
        employees = cursor.fetchall()

    return render(request, 'empl_list.html', {'employees': employees})


def edit_employee(request, id):
    return render(request, 'edit_employee.html')


def create_employee(surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, zip_code,
                    email, password):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO employees (surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city,zip_code, email, password) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)",
            [surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, zip_code, email,
             password])
