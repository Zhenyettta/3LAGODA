import json
from datetime import datetime, date
from functools import wraps

import bcrypt
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import LoginForm, EmployeeForm, EditEmployeeForm, CustomerForm, EditCustomerForm, CategoryForm, \
    EditCategoryForm, ProductForm, EditProductForm, InStoreProductForm, EditInStoreProductForm
from .user_data import User

user = User()


# TODO віктор абобус


def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if user.role == 'Sales':
            return HttpResponse(status=204)
        return view_func(request, *args, **kwargs)

    return wrapper


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
        query = "SELECT email, password, role, employee_id FROM employee"
        cursor.execute(query)
        logins = cursor.fetchall()
        for elem in logins:
            if elem[0] == email and bcrypt.checkpw(password, elem[1].tobytes()):
                user.email = email
                user.password = password
                user.role = elem[2]
                user.id = elem[3]
                return True
        return False


def home_page(request):
    if not user_is_manager():
        return render(request, 'sales/home.html')
    return HttpResponse(status=204)


@manager_required
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


def user_is_manager() -> object:
    return user.role == 'Manager'


def encryption():
    password = "123"
    password = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
    print(bcrypt.checkpw(password, hashedPassword))
    print(hashedPassword)
    with connection.cursor() as cursor:
        query = "UPDATE employee SET password = %s WHERE employee_id = %s", (hashedPassword, 2)
        cursor.execute(query)


@manager_required
def empl_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM employee WHERE email != %s ORDER BY surname, name, patronymic"
        cursor.execute(query, [user.email])
        employees = cursor.fetchall()

        context = {
            'employees': employees
        }
        return render(request, 'manager/employee/empl_list.html', context)


def my_info(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM employee WHERE email = %s"
        cursor.execute(query, [user.email])
        employee = cursor.fetchone()
    return render(request, 'sales/my_info/my_info.html', {'employee': employee})


@manager_required
def cust_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM customer_card ORDER BY surname, name, patronymic"
        cursor.execute(query)
        customers = cursor.fetchall()

        context = {
            'customers': customers
        }
        return render(request, 'manager/customers/cust_list.html', context)


def customers_view(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM customer_card ORDER BY surname, name, patronymic"
        cursor.execute(query)
        customers = cursor.fetchall()

    return render(request, 'sales/customers/customers_view.html', {'customers': customers})


def get_customer_by_name(request):
    name = request.GET.get('name').strip()
    with connection.cursor() as cursor:
        query = f"""SELECT * 
                    FROM customer_card 
                    WHERE surname LIKE '{name}%'
                    ORDER BY surname, name, patronymic"""

        cursor.execute(query)

        customers = cursor.fetchall()

    return render(request, 'sales/customers/customers_table.html', {'customers': customers})


@manager_required
def category_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM category ORDER BY name"
        cursor.execute(query)
        categories = cursor.fetchall()

        context = {
            'categories': categories
        }
        return render(request, 'manager/categories/category_list.html', context)


def fetch_products_and_categories():
    with connection.cursor() as cursor:
        query = """
            SELECT p.product_id, c.name, p.name, p.characteristics
            FROM product p
            JOIN category c ON p.category_number = c.category_number
            ORDER BY p.name
        """
        cursor.execute(query)
        products = cursor.fetchall()

        query = "SELECT c.name FROM category c"
        cursor.execute(query)
        categories = cursor.fetchall()

    return products, categories


@manager_required
def product_list(request):
    products, categories = fetch_products_and_categories()
    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'manager/products/product_list.html', context)


def product_view(request):
    products, categories = fetch_products_and_categories()
    context = {'products': products, 'categories': categories}
    return render(request, 'sales/products/product_view.html', context)

def find_check_view(request):
    return render(request, 'sales/find_check/find_check_view.html')

@manager_required
def get_products_by_category(request):
    category = request.GET.get('category')

    with connection.cursor() as cursor:
        query = """
            SELECT p.product_id, c.name, p.name, p.characteristics
            FROM product p
            JOIN category c ON p.category_number = c.category_number
            WHERE c.name = %s
            ORDER BY p.name
        """
        cursor.execute(query, [category])
        products = cursor.fetchall()

    html = render(request, 'manager/products/product_table.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})


def search_category(request):
    category = request.GET.get('category')
    with connection.cursor() as cursor:
        query = """
            SELECT p.product_id, c.name, p.name, p.characteristics
            FROM product p
            JOIN category c ON p.category_number = c.category_number
            WHERE c.name = %s
            ORDER BY p.name
            """
        cursor.execute(query, [category])
        products = cursor.fetchall()

    html = render(request, 'sales/products/product_view_table.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})


def get_product_by_name(request):
    name = request.GET.get('name')
    with connection.cursor() as cursor:
        query = f"""
            SELECT p.product_id, c.name, p.name, p.characteristics
            FROM product p
            JOIN category c ON p.category_number = c.category_number
            WHERE p.name LIKE '{name}%' 
            ORDER BY p.name
            """

        cursor.execute(query)
        products = cursor.fetchall()

    html = render(request, 'sales/products/product_view_table.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})


@manager_required
def get_in_store_by_upc(request):
    upc = request.GET.get('upc')

    with connection.cursor() as cursor:
        query = """
       SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional 
        FROM store_product s 
        JOIN product p on s.product_id = p.product_id
        WHERE s.upc LIKE %s
        ORDER BY s.count
        """

        cursor.execute(query, [upc + '%'])
        products = cursor.fetchall()

    html = render(request, 'manager/in_store_products/in_store_product_table.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})

def get_in_store_by_upc_sale(request):
    upc = request.GET.get('upc')

    with connection.cursor() as cursor:
        query = """
       SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional 
        FROM store_product s 
        JOIN product p on s.product_id = p.product_id
        WHERE s.upc LIKE %s
        ORDER BY s.count
        """

        cursor.execute(query, [upc + '%'])
        products = cursor.fetchall()

    html = render(request, 'sales/in_store_products/in_store_table_view.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})



@manager_required
def get_customer_by_percent(request):
    prom = request.GET.get('prom')
    with connection.cursor() as cursor:
        query = """
        SELECT *
        FROM customer_card
        WHERE percent = %s
        """
        cursor.execute(query, [prom])
        customers = cursor.fetchall()

    html = render(request, 'manager/customers/customer_table.html', {'customers': customers}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})


@manager_required
def get_empl_by_surname(request):
    surname = request.GET.get('surname')
    with connection.cursor() as cursor:
        query = """
            SELECT *
            FROM employee e
            WHERE e.surname LIKE %s
            ORDER BY surname, name, patronymic
            """
        cursor.execute(query, ['%' + surname + '%'])
        employees = cursor.fetchall()

    html = render(request, 'manager/employee/empl_table.html', {'employees': employees}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})


@manager_required
def check_list(request):
    with connection.cursor() as cursor:
        query = """
            SELECT c.check_number, e.surname || ' ' || e.name || ' ' || e.patronymic || '(id:' || e.employee_id || ')'
            , c.card_number, c.print_date, c.sum_total, c.vat
            FROM "check" c
            JOIN employee e ON c.employee_id = e.employee_id
            ORDER BY c.print_date desc
        """
        cursor.execute(query)
        checks = cursor.fetchall()
        query_empl = """
            SELECT *
            FROM employee
        """
        cursor.execute(query_empl)
        employees = cursor.fetchall()

    context = {'checks': checks, 'employees': employees}

    return render(request, 'manager/checks/check_list.html', context)


def today_check(request):
    today = date.today()
    formatted_date = datetime.strptime(str(today), '%Y-%m-%d').date()

    with connection.cursor() as cursor:
        query = """
            SELECT c.check_number, c.card_number, c.print_date, c.sum_total, c.vat
            FROM "check" c
            JOIN employee e ON c.employee_id = e.employee_id
            WHERE e.email = %s AND DATE(c.print_date AT TIME ZONE 'UTC')::date = %s
            ORDER BY c.print_date desc
        """

        cursor.execute(query, [user.email, formatted_date])
        checks = cursor.fetchall()

    context = {'checks': checks}

    return render(request, 'sales/my_info/checks_table.html', context)

def found_check_info(request):
    checkNumber = request.GET.get('check_number')

    with connection.cursor() as cursor:
        query = """
            SELECT c.check_number, e.surname || ' ' || e.name || ' ' || e.patronymic, c.card_number, c.print_date, c.sum_total, c.vat
            FROM "check" c
            JOIN employee e ON c.employee_id = e.employee_id
            WHERE c.check_number = %s
            ORDER BY c.print_date desc
        """

        cursor.execute(query, [checkNumber])
        checks = cursor.fetchall()

        query1 = """
        SELECT s.upc, p.name, s.price, s.product_count FROM sale s
        JOIN store_product on s.upc = store_product.upc
        JOIN product p on p.product_id = store_product.product_id
        WHERE check_number = %s
        """
        cursor.execute(query1, [checkNumber])
        sales = cursor.fetchall()

    context = {'checks': checks, 'sales':sales}

    return render(request, 'sales/find_check/found_check.html', context)

def date_working_checks(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print(start_date, end_date)
    with connection.cursor() as cursor:
        query = """
            SELECT c.check_number, c.card_number, c.print_date, c.sum_total, c.vat
            FROM "check" c
            JOIN employee e ON c.employee_id = e.employee_id
            WHERE e.email = %s AND DATE(c.print_date AT TIME ZONE 'UTC')::date BETWEEN %s AND %s
            ORDER BY c.print_date desc
        """

        cursor.execute(query, [user.email, start_date, end_date])
        checks = cursor.fetchall()

    context = {'checks': checks}
    return render(request, 'sales/my_info/checks_table.html', context)


@manager_required
def in_store_product_list(request):
    with connection.cursor() as cursor:
        query = """
        SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional 
        FROM store_product s 
        JOIN product p on s.product_id = p.product_id
        ORDER BY s.count
        """
        cursor.execute(query)
        in_store_products = cursor.fetchall()

        query = """SELECT MIN(product_id), name
                    FROM product
                    GROUP BY name
                    ORDER BY name
                    """

        cursor.execute(query)
        prod_name = cursor.fetchall()

        context = {
            'products': in_store_products,
            'prod_name': prod_name,
        }

    return render(request, 'manager/in_store_products/in_store_product_list.html', context)


def instoreproducts_view(request):
    with connection.cursor() as cursor:
        query = """
        SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional 
        FROM store_product s 
        JOIN product p on s.product_id = p.product_id
        ORDER BY s.count
        """
        cursor.execute(query)
        in_store_products = cursor.fetchall()

        query = """SELECT MIN(product_id), name
                    FROM product
                    GROUP BY name
                    ORDER BY name
                    """

        cursor.execute(query)
        prod_name = cursor.fetchall()

        context = {
            'products': in_store_products,
            'prod_name': prod_name,

        }
    return render(request, 'sales/in_store_products/in_store_view.html', context)


@manager_required
def empl_only_sales_list(request):
    with connection.cursor() as cursor:
        query = """
        SELECT * FROM employee 
        WHERE role='Sales' 
        ORDER BY surname, name, patronymic
        """
        cursor.execute(query)
        employees = cursor.fetchall()

    html = render(request, 'manager/employee/empl_table.html', {'employees': employees}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})


@manager_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if is_email_used(data['email']):
                error_message = 'Email is already used by another user.'
                return render(request, 'manager/employee/add_employee.html',
                              {'form': form, 'error_message': error_message})

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
            return redirect('empl_list')
    else:
        form = EmployeeForm()
    return render(request, 'manager/employee/add_employee.html', {'form': form})


@manager_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            for key, value in data.items():
                if value == "":
                    data[key] = None
            create_customer(
                data['surname'],
                data['name'],
                data['patronymic'],
                data['phone_number'],
                data['city'],
                data['street'],
                data['zip_code'],
                data['percent'],
            )
            return redirect('cust_list')
    else:
        form = CustomerForm()
    return render(request, 'manager/customers/add_customer.html', {'form': form})


@manager_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_category(
                data['name'],
            )
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'manager/categories/add_category.html', {'form': form})


@manager_required
def add_product(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM category"
        cursor.execute(query)
        categories = cursor.fetchall()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_product(
                data['category'],
                data['name'],
                data['characteristics'],
            )
            return redirect('product_list')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'manager/products/add_product.html', context)


@manager_required
def add_in_store_product(request):
    with connection.cursor() as cursor:
        query = f"""SELECT * FROM product p
        where p.product_id not in (SELECT sp2.product_id FROM store_product sp2)
        """
        cursor.execute(query)
        products = cursor.fetchall()

    if request.method == 'POST':
        form = InStoreProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_in_store_product(
                data['id'],
                data['price'],
                data['count'],
                data['prom'],
                data['upc'],
            )
            return redirect('in_store_product_list')
        else:
            print(form.errors)
    else:
        form = ProductForm()

    context = {
        'form': form,
        'products': products,
    }
    return render(request, 'manager/in_store_products/add_in_store_product.html', context)


def is_email_used(email):
    with connection.cursor() as cursor:
        query = "SELECT COUNT(*) FROM employee WHERE email = %s"
        cursor.execute(query, [email])
        result = cursor.fetchone()
        count = result[0]
        return count > 0


@manager_required
def delete_employee(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM employee WHERE employee_id = %s"
        cursor.execute(query, [id])
    return redirect('/manager/employees')


@manager_required
def delete_customer(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM customer_card WHERE card_number = %s"
        cursor.execute(query, [id])
    return redirect('/manager/customers')


@manager_required
def delete_customer_as_sale(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM customer_card WHERE card_number = %s"
        cursor.execute(query, [id])
    return redirect('/home/customers_view')


@manager_required
def delete_category(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM category WHERE category_number = %s"
        cursor.execute(query, [id])
    return redirect('/manager/categories')


@manager_required
def delete_product(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM product WHERE product_id = %s"
        cursor.execute(query, [id])
    return redirect('/manager/products')


@manager_required
def delete_in_store_product(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM store_product WHERE product_id = %s"
        cursor.execute(query, [id])
    return redirect('/manager/instoreproducts')


@manager_required
def delete_check(request, id):
    with connection.cursor() as cursor:
        query = 'DELETE FROM "check" WHERE check_number = %s'
        cursor.execute(query, [id])

    return redirect('/manager/checks')


@manager_required
def watch_check(request, id):
    with connection.cursor() as cursor:
        query = """
        SELECT s.upc, p.name, s.price, s.product_count FROM sale s
        JOIN store_product on s.upc = store_product.upc
        JOIN product p on p.product_id = store_product.product_id
        WHERE check_number = %s
        """
        cursor.execute(query, [id])
        sales = cursor.fetchall()
    return render(request, 'manager/checks/watch_check.html', {'sales': sales})


@manager_required
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
            return redirect('empl_list')

    else:
        with connection.cursor() as cursor:
            query = """
                SELECT employee_id, surname, name, patronymic, role, salary, date_of_birth, date_of_start,
                phone_number, city, street, zip_code, email FROM employee WHERE employee_id = %s"""
            cursor.execute(query, [id])
            employee = cursor.fetchone()
    return render(request, 'manager/employee/edit_employee.html', {'employee': employee})


@manager_required
def edit_customer_button(request, id):
    if request.method == 'POST':
        form = EditCustomerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_customer(
                id,
                data['surname'],
                data['name'],
                data['patronymic'],
                data['phone_number'],
                data['city'],
                data['street'],
                data['zip_code'],
                data['percent'])
            return redirect('cust_list')

    else:
        customer_query = """
            SELECT card_number, surname, name, patronymic, phone_number, city, street, zip_code, percent
            FROM customer_card
            WHERE card_number = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(customer_query, [id])
            customer = cursor.fetchone()
    return render(request, 'manager/customers/edit_customer.html', {'customer': customer})


def edit_customer_button_sales(request, id):
    if request.method == 'POST':
        form = EditCustomerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_customer(
                id,
                data['surname'],
                data['name'],
                data['patronymic'],
                data['phone_number'],
                data['city'],
                data['street'],
                data['zip_code'],
                data['percent'])
            return redirect('customers_view')

    else:
        customer_query = """
            SELECT card_number, surname, name, patronymic, phone_number, city, street, zip_code, percent
            FROM customer_card
            WHERE card_number = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(customer_query, [id])
            customer = cursor.fetchone()
    return render(request, 'sales/customers/edit_cust_from_sale.html', {'customer': customer})


@manager_required
def edit_category_button(request, id):
    if request.method == 'POST':
        form = EditCategoryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_category(
                id,
                data['name'])
            return redirect('category_list')
    else:
        category_query = """
            SELECT name
            FROM category
            WHERE category_number = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(category_query, [id])
            category = cursor.fetchone()
    return render(request, 'manager/categories/edit_category.html', {'category': category})


@manager_required
def edit_product_button(request, id):
    if request.method == 'POST':
        form = EditProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_product(
                id,
                data['category'],
                data['name'],
                data['characteristics'])
            return redirect('product_list')
    else:
        product_query = """
            SELECT category_number, name, characteristics
            FROM product
            WHERE product_id = %s
        """
        category_query = "SELECT * FROM category"
        with connection.cursor() as cursor:
            cursor.execute(product_query, [id])
            product = cursor.fetchone()
            cursor.execute(category_query)
            categories = cursor.fetchall()
            context = {
                'product': product,
                'categories': categories
            }

    return render(request, 'manager/products/edit_product.html', context)


@manager_required
def edit_in_store_product_button(request, id):
    if request.method == 'POST':
        form = EditInStoreProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_in_store_product(
                id,
                data['price'],
                data['count'],
                data['upc'],
                data['prom'],
            )
            return redirect('in_store_product_list')
    else:
        product_query = """
            SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional
            FROM store_product s 
            JOIN product p on s.product_id = p.product_id
            WHERE s.product_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(product_query, [id])
            product = cursor.fetchone()

            context = {
                'product': product
            }

    return render(request, 'manager/in_store_products/edit_in_store_product.html', context)


@manager_required
def create_employee(surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
                    zip_code,
                    email, password):
    employee_query = """
        INSERT INTO employee (surname, name, patronymic, role, salary, date_of_birth,
        date_of_start, phone_number, city, street, zip_code, email, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            employee_query,
            [surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
             zip_code, email, password]
        )


def create_customer(surname, name, patronymic, phone_number, city, street, zip_code, percent):
    customer_query = """
        INSERT INTO customer_card (surname, name, patronymic, phone_number, city, street, zip_code, percent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            customer_query,
            [surname, name, patronymic, phone_number, city, street, zip_code, percent]
        )


def create_category(name):
    category_query = "INSERT INTO category (name) VALUES (%s)"
    with connection.cursor() as cursor:
        cursor.execute(category_query, [name])


def create_product(category, name, characteristics):
    with connection.cursor() as cursor:
        query = """
        INSERT INTO product (category_number, name, characteristics)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, [category, name, characteristics])


def create_in_store_product(id, price, count, is_promotional, upc):
    with connection.cursor() as cursor:
        query = """
        INSERT INTO store_product (product_id, price, count, is_promotional, upc)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, [id, price, count, is_promotional, upc])


def edit_employee(id, surname, name, patronymic, role, salary, date_of_birth, date_of_start, phone_number, city, street,
                  zip_code, email, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None
    with connection.cursor() as cursor:
        if role == "":
            cursor.execute("SELECT role FROM employee where employee_id =%s", [id])
            role = cursor.fetchall()[0]
        if password:
            query = """
            UPDATE employee
            SET surname = %s, name = %s, patronymic = %s, role = %s, salary = %s,
            date_of_birth = %s, date_of_start = %s, phone_number = %s, city = %s, street = %s, zip_code = %s,
            email = %s, password = %s
            WHERE employee_id = %s
            """
            cursor.execute(query, [surname, name, patronymic, role, salary, date_of_birth, date_of_start,
                                   phone_number, city, street, zip_code, email, hashed_password, id])
        else:
            query = """
            UPDATE employee
            SET surname = %s, name = %s, patronymic = %s, role = %s, salary = %s,
            date_of_birth = %s, date_of_start = %s, phone_number = %s, city = %s, street = %s, zip_code = %s,
            email = %s
            WHERE employee_id = %s
            """
            cursor.execute(query, [surname, name, patronymic, role, salary, date_of_birth, date_of_start,
                                   phone_number, city, street, zip_code, email, id])


def edit_customer(id, surname, name, patronymic, phone_number, city, street, zip_code, percent):
    if city.strip() == "":
        city = None
    if street.strip() == "":
        street = None
    if zip_code.strip() == "":
        zip_code = None

    with connection.cursor() as cursor:
        query = """
        UPDATE customer_card
        SET surname = %s, name = %s, patronymic = %s,
        phone_number = %s, city = %s, street = %s, zip_code = %s,
        percent = %s
        WHERE card_number = %s
        """
        cursor.execute(query, [surname, name, patronymic, phone_number, city, street, zip_code, percent, id])


def edit_category(id, name):
    with connection.cursor() as cursor:
        query = """
        UPDATE category
        SET name = %s
        WHERE category_number = %s
        """
        cursor.execute(query, [name, id])


def edit_product(id, category, name, characteristics):
    with connection.cursor() as cursor:
        query = """
        UPDATE product SET category_number = %s, name = %s, characteristics = %s WHERE product_id = %s
        """
        cursor.execute(query, [category, name, characteristics, id])


def edit_in_store_product(id, price, count, upc, prom):
    with connection.cursor() as cursor:
        query = """
        UPDATE store_product SET price = %s, count = %s, upc = %s, is_promotional = %s WHERE product_id = %s
        """
        cursor.execute(query, [price, count, upc, prom, id])


def sale(request):
    with connection.cursor() as cursor:
        query = """
        SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional 
        FROM store_product s 
        JOIN product p on s.product_id = p.product_id
        """
        cursor.execute(query)
        in_store_products = cursor.fetchall()
    return render(request, 'sales/create_check.html', {'products': in_store_products})


def create_check(request):
    if request.method == 'GET':
        data = request.GET.get('data')
        if data is not None:
            data = json.loads(data)
            price = sum(float(item[3]) * int(item[4]) for item in data)

            with connection.cursor() as cursor:
                query = """
                    INSERT INTO "check" (employee_id, card_number, sum_total, vat)
                    VALUES (%s, %s, %s, %s)
                    RETURNING check_number;
                """
                cursor.execute(query, [user.id, 2, price, 20])
                check_number = cursor.fetchone()[0]

                query_sale = """
                    INSERT INTO sale (upc, price, check_number, product_count)
                    VALUES (%s, %s, %s, %s);
                """
                cursor.executemany(query_sale, [(item[0], item[3], check_number, item[4]) for item in data])

                query = """
                    SELECT c.check_number, e.surname || ' ' || e.name || ' ' || e.patronymic || '(id:' || e.employee_id || ')',
                    c.card_number, c.print_date, c.sum_total, c.vat
                    FROM "check" c
                    JOIN employee e ON c.employee_id = e.employee_id
                    ORDER BY c.print_date desc
                """
                cursor.execute(query)
                checks = cursor.fetchall()

                context = {'checks': checks}

                return redirect('sale')
    return JsonResponse({'error': 'Invalid request method'})


@manager_required
def sort_selected(request):
    choice = request.GET.get('choice')
    prom = request.GET.get('prom')
    order = request.GET.get('order')

    with connection.cursor() as cursor:
        query = f"""
            SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional
            FROM store_product s
            JOIN product p on s.product_id = p.product_id
            WHERE is_promotional IN ({prom})
            ORDER BY {choice} {order}
            """

        cursor.execute(query)
        products = cursor.fetchall()

    html = render(request, 'manager/in_store_products/in_store_product_table.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})

def sale_sort_selected(request):
    choice = request.GET.get('choice')
    prom = request.GET.get('prom')
    order = request.GET.get('order')
    print(f"1:{choice}, 2:{prom}, 3:{order}")

    with connection.cursor() as cursor:
        query = f"""
            SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional
            FROM store_product s
            JOIN product p on s.product_id = p.product_id
            WHERE is_promotional IN ({prom})
            ORDER BY {choice} {order}
            """

        cursor.execute(query)
        products = cursor.fetchall()

    html = render(request, 'sales/in_store_products/in_store_table_view.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})

@manager_required
def get_all_checks_all_empl(request):
    start_date = request.GET.get('start_date')
    parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = request.GET.get('end_date')
    parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    employee = request.GET.get('empl_id')

    if employee == 'all':
        with connection.cursor() as cursor:
            query = f"""
                SELECT c.check_number, e.surname || ' ' || e.name || ' ' || e.patronymic || '(id:' || e.employee_id || ')'
                , c.card_number, c.print_date, c.sum_total, c.vat
                FROM "check" c
                JOIN employee e ON c.employee_id = e.employee_id
                WHERE DATE(c.print_date AT TIME ZONE 'UTC')::date BETWEEN '{parsed_start_date}' AND '{parsed_end_date}'
                ORDER BY c.print_date desc
            """
            cursor.execute(query)
            checks = cursor.fetchall()
    else:
        with connection.cursor() as cursor:
            query = f"""
                SELECT c.check_number, e.surname || ' ' || e.name || ' ' || e.patronymic || '(id:' || e.employee_id || ')'
                , c.card_number, c.print_date, c.sum_total, c.vat
                FROM "check" c
                JOIN employee e ON c.employee_id = e.employee_id
                WHERE c.employee_id = {employee} AND DATE(c.print_date AT TIME ZONE 'UTC')::date BETWEEN '{parsed_start_date}' AND '{parsed_end_date}'
                ORDER BY c.print_date desc
            """
            cursor.execute(query)
            checks = cursor.fetchall()

    html = render(request, 'manager/checks/check_table.html', {'checks': checks}).content
    html = html.decode('utf-8')

    return JsonResponse({'html': html})


@manager_required
def get_all_checks_sum(request):
    start_date = request.GET.get('start_date')
    parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = request.GET.get('end_date')
    parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    employee = request.GET.get('empl_id')
    if employee == 'all':
        with connection.cursor() as cursor:
            query = f"""
                SELECT e.surname || ' ' || e.name || ' ' || e.patronymic, SUM(c.sum_total)
                FROM "check" c
                JOIN employee e ON c.employee_id = e.employee_id
                WHERE DATE(c.print_date AT TIME ZONE 'UTC')::date BETWEEN '{parsed_start_date}' AND '{parsed_end_date}'
                GROUP BY e.surname, e.name, e.patronymic
            """

            cursor.execute(query)
            checks = cursor.fetchall()
    else:
        with connection.cursor() as cursor:
            query = f"""
                SELECT e.surname || ' ' || e.name || ' ' || e.patronymic, SUM(c.sum_total)
                FROM "check" c
                JOIN employee e ON c.employee_id = e.employee_id
                WHERE c.employee_id = {employee} AND DATE(c.print_date AT TIME ZONE 'UTC')::date 
                BETWEEN '{parsed_start_date}' AND '{parsed_end_date}'
                GROUP BY e.surname, e.name, e.patronymic
            """

            cursor.execute(query)
            checks = cursor.fetchall()

    html = render(request, 'manager/checks/check_sum_table.html', {'checks': checks}).content
    html = html.decode('utf-8')

    return JsonResponse({'html': html})


@manager_required
def find_product(request):
    product = request.GET.get('product')
    start_date = request.GET.get('requested_date')
    end_date = request.GET.get('requested_date_end')

    parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    with connection.cursor() as cursor:
        query = f"""
            SELECT SUM(sp.count), p.name AS total_units_sold
            FROM Sale s
            JOIN "check" c ON s.check_number = c.check_number
            JOIN store_product sp ON s.UPC = sp.UPC
            JOIN product p ON p.product_id = sp.product_id
            WHERE p.name = '{product}'
            AND DATE(c.print_date AT TIME ZONE 'UTC')::date BETWEEN '{parsed_start_date}' AND '{parsed_end_date}'
            GROUP BY p.name
        """
        cursor.execute(query)
        products = cursor.fetchall()

    html = render(request, 'manager/in_store_products/in_store_sum.html', {'products': products}).content
    html = html.decode('utf-8')
    return JsonResponse({'html': html})
