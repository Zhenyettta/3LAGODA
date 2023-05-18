import bcrypt
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import LoginForm, EmployeeForm, EditEmployeeForm
from .user_data import User

user = User()


def show_form(request):
    form = LoginForm()
    return render(request, 'login/login.html', {"form": form})


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
        return render(request, 'sales/home.html')
    return HttpResponse(status=204)


def manager_page(request):
    if user_is_manager():
        return render(request, 'manager/manager.html')
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
        cursor.execute("SELECT * FROM employee WHERE email != %s ORDER BY surname, name, patronymic", [user.email])
        employees = cursor.fetchall()

    return render(request, 'manager/employee/empl_list.html', {'employees': employees})

def cust_list(request):
    return render(request, 'manager/customers/cust_list.html')

def category_list(request):
    return render(request, 'manager/categories/category_list.html')

def product_list(request):
    return render(request, 'manager/products/product_list.html')

def in_store_product_list(request):
    return render(request, 'manager/in_store_products/in_store_product_list.html')

def cust_list(request):
    return render(request, 'manager/customers/cust_list.html')

def empl_only_sales_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM employee WHERE role='Sales' ORDER BY surname, name, patronymic")
        employees = cursor.fetchall()

    return render(request, 'manager/employee/empl_list.html', {'employees': employees})


def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if is_email_used(data['email']):
                error_message = 'Email is already used by another user.'
                return render(request, 'manager/add_employee.html', {'form': form, 'error_message': error_message})

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
                data['street'],
                data['zip_code'],
                data['email'],
                bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            )
            return empl_list(request)
    else:
        form = EmployeeForm()
    return render(request, 'manager/employee/add_employee.html', {'form': form})


def is_email_used(email):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM employee WHERE email = %s", [email])
        result = cursor.fetchone()
        count = result[0]
        return count > 0


def delete_employee(request, id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM employee WHERE employee_id = %s", [id])
        cursor.execute("SELECT * FROM employee WHERE role = 'Sales'")
        employees = cursor.fetchall()
    return redirect('/manager/employees')


def edit_employee_button(request, id):
    if request.method == 'POST':
        form = EditEmployeeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_employee(
                id,
                data['surname'],
                data['name'],
                data['patronymic'],
                data['role'],
                data['salary'],
                data['date_of_birth'],
                data['date_of_start'],
                data['phone_number'],
                data['city'],
                data['street'],
                data['zip_code'],
                data['email'],
                data['password'])
            return empl_list(request)

    else:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT employee_id, surname, name, patronymic, role, salary, date_of_birth, date_of_start,"
                " phone_number, city, street, zip_code, email FROM employee WHERE employee_id = %s",
                [id])
            employee = cursor.fetchone()
    return render(request, 'manager/employee/edit_employee.html', {'employee': employee})


def create_employee(surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
                    zip_code,
                    email, password):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO employee (surname, name, patronymic, role, salary, date_of_birth,"
            " date_of_start, phone_number, city,street,zip_code, email, password)"
            " VALUES (%s, %s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s, %s)",
            [surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
             zip_code, email,
             password])


def edit_employee(id, surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
                  zip_code, email, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None
    with connection.cursor() as cursor:
        if password:
            cursor.execute(
                "UPDATE employee SET surname = %s, name = %s, patronymic = %s, role = %s, salary = %s, "
                "date_of_birth = %s, date_of_start = %s, phone_number = %s, city = %s, street = %s, zip_code = %s, "
                "email = %s, password = %s WHERE employee_id = %s;",
                [surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
                 zip_code, email, hashed_password, id])
        else:
            cursor.execute(
                "UPDATE employee SET surname = %s, name = %s, patronymic = %s, role = %s, salary = %s, "
                "date_of_birth = %s, date_of_start = %s, phone_number = %s, city = %s, street = %s, zip_code = %s, "
                "email = %s WHERE employee_id = %s;",
                [surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
                 zip_code, email, id])
