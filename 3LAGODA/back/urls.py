"""
URL configuration for back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from back import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login
    path('', views.show_form),
    path('submit_form/', views.submit_form, name='submit_form'),

    # Manager
    path('manager/', views.manager_page, name='manager_page'),

    # Employee list manipulations
    path('manager/employees/', views.empl_list, name='empl_list'),
    path('manager/employees/addemployee/', views.add_employee, name='add_employee'),
    path('manager/employees/edit/<int:id>/', views.edit_employee_button, name='edit_employee'),
    path('manager/employees/<int:id>/delete/', views.delete_employee, name='delete_employee'),
    path('manager/employees/onlysales/', views.empl_only_sales_list, name='empl_only_sales_list'),
    path('manager/employees/get_empl_by_surname/', views.get_empl_by_surname, name='get_empl_by_surname'),
    path('manager/employees/empl_counts/', views.empl_counts, name='empl_counts'),

    # Customer list implementation
    path('manager/customers/', views.cust_list, name='cust_list'),
    path('manager/customers/addcustomer', views.add_customer, name='add_customer'),
    path('manager/customers/edit/<int:id>/', views.edit_customer_button, name='manager_edit_customer'),
    path('manager/customers/<int:id>/delete/', views.delete_customer, name='delete_customer'),
    path('manager/customers/get_customer_by_percent/', views.get_customer_by_percent, name='get_customer_by_percent'),

    # Category list implementation
    path('manager/categories/', views.category_list, name='category_list'),
    path('manager/categories/addcategory', views.add_category, name='add_category'),
    path('manager/categories/edit/<int:id>/', views.edit_category_button, name='edit_category'),
    path('manager/categories/<int:id>/delete/', views.delete_category, name='delete_category'),
    path('manager/categories/find_category', views.find_category, name='find_category'),

    # Product list implementation
    path('manager/products/', views.product_list, name='product_list'),
    path('manager/products/addproduct', views.add_product, name='add_product'),
    path('manager/products/edit/<int:id>/', views.edit_product_button, name='edit_product'),
    path('manager/products/<int:id>/delete/', views.delete_product, name='delete_product'),
    path('manager/products/get_products_by_category/', views.get_products_by_category, name='get_products_by_category'),
    path('manager/products/get_product_by_name_manager/', views.get_product_by_name,
         name='get_product_by_name_manager'),

    # InStoreProduct list implementation
    path('manager/instoreproducts/', views.in_store_product_list, name='in_store_product_list'),
    path('manager/instoreproducts/addproduct', views.add_in_store_product, name='add_in_store_product'),
    path('manager/instoreproducts/edit/<int:id>/', views.edit_in_store_product_button, name='edit_in_store_product'),
    path('manager/instoreproducts/<int:id>/delete', views.delete_in_store_product, name='delete_in_store_product'),
    path('manager/instoreproducts/get_in_store_by_upc/', views.get_in_store_by_upc, name='get_in_store_by_upc'),

    path('manager/instoreproducts/sort_selected/', views.sort_selected, name='sort_selected'),
    path('manager/instoreproducts/find_product/', views.find_product, name='find_product'),

    # Check list implementation
    path('manager/checks/', views.check_list, name='check_list'),
    path('manager/checks/<int:id>/delete/', views.delete_check, name='delete_check'),
    path('manager/checks/watch/<int:id>/', views.watch_check, name='watch_check'),
    path('manager/checks/get_all_checks_all_empl/', views.get_all_checks_all_empl, name='get_all_checks_all_empl'),
    path('manager/checks/get_all_checks_sum/', views.get_all_checks_sum, name='get_all_checks_sum'),

    # Sales
    path('home/', views.home_page, name='home_page'),

    #Products
    path('home/product_view/', views.product_view, name='product_view'),
    path('home/product_view/search_category/', views.search_category, name='search_category'),
    path('home/product_view/get_product_by_name/', views.get_product_by_name, name='get_product_by_name'),

    # In Store
    path('home/instoreproducts_view/', views.instoreproducts_view, name='instoreproducts_view'),
    path('home/instoreproducts_view/sale_sort_selected/', views.sale_sort_selected, name='sale_sort_selected'),
    path('home/instoreproducts_view/get_in_store_by_upc_sale/', views.get_in_store_by_upc_sale,
         name='get_in_store_by_upc_sale'),

    # Customers
    path('home/customers_view/', views.customers_view, name='customers_view'),
    path('home/customers/addcustomer', views.add_customer_sales, name='add_customer'),
    path('home/customers_view/edit/<int:id>/', views.edit_customer_button_sales, name='edit_customer'),
    path('home/customers_view/<int:id>/delete/', views.delete_customer_as_sale, name='delete_customer'),
    path('home/customers_list/get_customer_by_name/', views.get_customer_by_name, name='get_customer_by_name'),

    path('home/sale/', views.sale, name='sale'),
    path('home/sale/createcheck/', views.create_check, name='create_check'),

    path('home/my_info/', views.my_info, name='my_info'),
    path('home/my_info/today_check/', views.today_check, name='today_check'),
    path('home/my_info/date_working_checks/', views.date_working_checks, name='date_working_checks'),


    path('home/find_check_view/', views.find_check_view, name='find_check_view'),
    path('home/find_check_view/found_check', views.found_check_info, name='found_check_info'),

]
