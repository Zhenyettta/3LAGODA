import json

import bcrypt
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import LoginForm, EmployeeForm, EditEmployeeForm, CustomerForm, EditCustomerForm, CategoryForm, \
    EditCategoryForm, ProductForm, EditProductForm, InStoreProductForm, EditInStoreProductForm
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
        query = "UPDATE employee SET password = %s WHERE employee_id = %s", (hashedPassword, 2)
        cursor.execute(query)


def empl_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM employee WHERE email != %s ORDER BY surname, name, patronymic"
        cursor.execute(query, [user.email])
        employees = cursor.fetchall()

    return render(request, 'manager/employee/empl_list.html', {'employees': employees})


def cust_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM customer_card ORDER BY surname, name, patronymic"
        cursor.execute(query)
        customers = cursor.fetchall()
        updated_list = []
        for tpl in customers:
            updated_tuple = list(tpl)
            if updated_tuple[3] is None:
                updated_tuple[3] = ""
            updated_list.append(tuple(updated_tuple))
    return render(request, 'manager/customers/cust_list.html', {'customers': updated_list})


def category_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM category ORDER BY name"
        cursor.execute(query)
        categories = cursor.fetchall()

    return render(request, 'manager/categories/category_list.html', {'categories': categories})


def product_list(request):
    with connection.cursor() as cursor:
        query = """
            SELECT p.product_id, c.name, p.name, p.characteristics
            FROM product p
            JOIN category c ON p.category_number = c.category_number
            ORDER BY p.name
        """
        cursor.execute(query)
        products = cursor.fetchall()

    products = {'products': products}
    return render(request, 'manager/products/product_list.html', products)


def check_list(request):
    with connection.cursor() as cursor:
        query = """
            SELECT c.check_number, e.surname || ' ' || e.name || ' ' || e.patronymic || '(id:' || e.employee_id || ')'
            , c.card_number, c.print_date, c.sum_total, c.vat
            FROM "check" c
            JOIN employee e ON c.employee_id = e.employee_id
        """
        cursor.execute(query)
        modified_checks = cursor.fetchall()

    context = {'checks': modified_checks}
    return render(request, 'manager/checks/check_list.html', context)


def in_store_product_list(request):
    with connection.cursor() as cursor:
        query = """
        SELECT s.upc, s.product_id, p.name, s.price, s.count, s.is_promotional 
        FROM store_product s 
        JOIN product p on s.product_id = p.product_id
        """
        cursor.execute(query)
        in_store_products = cursor.fetchall()
    return render(request, 'manager/in_store_products/in_store_product_list.html', {'products': in_store_products})


def empl_only_sales_list(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM employee WHERE role='Sales' ORDER BY surname, name, patronymic"
        cursor.execute(query)
        employees = cursor.fetchall()

    return render(request, 'manager/employee/empl_list.html', {'employees': employees})


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
            return empl_list(request)
    else:
        form = EmployeeForm()
    return render(request, 'manager/employee/add_employee.html', {'form': form})


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
            return cust_list(request)
    else:
        form = CustomerForm()
    return render(request, 'manager/customers/add_customer.html', {'form': form})


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            create_category(
                data['name'],
            )
            return category_list(request)
    else:
        form = CategoryForm()
    return render(request, 'manager/categories/add_category.html', {'form': form})


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
            return product_list(request)
    else:
        form = ProductForm()

    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'manager/products/add_product.html', context)


def add_in_store_product(request):
    with connection.cursor() as cursor:
        query = "SELECT * FROM product"
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
            return in_store_product_list(request)
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


def delete_employee(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM employee WHERE employee_id = %s"
        cursor.execute(query, [id])
    return redirect('/manager/employees')


def delete_customer(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM customer_card WHERE card_number = %s"
        cursor.execute(query, [id])
    return redirect('/manager/customers')


def delete_category(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM category WHERE category_number = %s"
        cursor.execute(query, [id])
    return redirect('/manager/categories')


def delete_product(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM product WHERE product_id = %s"
        cursor.execute(query, [id])
    return redirect('/manager/products')


def delete_in_store_product(request, id):
    with connection.cursor() as cursor:
        query = "DELETE FROM store_product WHERE product_id = %s"
        cursor.execute(query, [id])
    return redirect('/manager/instoreproducts')


def delete_check(request, id):
    with connection.cursor() as cursor:
        query = 'DELETE FROM "check" WHERE check_number = %s'
        cursor.execute(query, [id])

    return redirect('/manager/checks')


def watch_check(request, id):
    with connection.cursor() as cursor:
        query = 'SELECT * FROM sale WHERE check_number = %s'
        cursor.execute(query, [id])
        sales = cursor.fetchall()
    return render(request, 'manager/checks/watch_check.html', {'sales': sales})


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
            query = """
                SELECT employee_id, surname, name, patronymic, role, salary, date_of_birth, date_of_start,
                phone_number, city, street, zip_code, email FROM employee WHERE employee_id = %s"""
            cursor.execute(query, [id])
            employee = cursor.fetchone()
    return render(request, 'manager/employee/edit_employee.html', {'employee': employee})


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
            return cust_list(request)

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


def edit_category_button(request, id):
    if request.method == 'POST':
        form = EditCategoryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_category(
                id,
                data['name'])
            return category_list(request)
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
            return product_list(request)
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
            return in_store_product_list(request)
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
    return render(request, 'manager/sale.html', {'products': in_store_products})


def create_check(request):
    if request.method == 'POST':
        data = request.POST.get('data')
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

    return check_list(request)