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

    path('manager/sale/', views.sale, name='sale'),
    path('manager/sale/createcheck/', views.create_check, name='create_check'),

    # Employee list manipulations
    path('manager/employees/', views.empl_list, name='empl_list'),
    path('manager/employees/addemployee/', views.add_employee, name='add_employee'),
    path('manager/employees/edit/<int:id>/', views.edit_employee_button, name='edit_employee'),
    path('manager/employees/<int:id>/delete/', views.delete_employee, name='delete_employee'),
    path('manager/employees/onlysales/', views.empl_only_sales_list, name='empl_only_sales_list'),
    path('manager/employees/get_empl_by_surname/', views.get_empl_by_surname, name='get_empl_by_surname'),

    # Customer list implementation
    path('manager/customers/', views.cust_list, name='cust_list'),
    path('manager/customers/addcustomer', views.add_customer, name='add_customer'),
    path('manager/customers/edit/<int:id>/', views.edit_customer_button, name='edit_customer'),
    path('manager/customers/<int:id>/delete/', views.delete_customer, name='delete_customer'),

    # Category list implementation
    path('manager/categories/', views.category_list, name='category_list'),
    path('manager/categories/addcategory', views.add_category, name='add_category'),
    path('manager/categories/edit/<int:id>/', views.edit_category_button, name='edit_category'),
    path('manager/categories/<int:id>/delete/', views.delete_category, name='delete_category'),

    # Product list implementation
    path('manager/products/', views.product_list, name='product_list'),
    path('manager/products/addproduct', views.add_product, name='add_product'),
    path('manager/products/edit/<int:id>/', views.edit_product_button, name='edit_product'),
    path('manager/products/<int:id>/delete/', views.delete_product, name='delete_product'),
    path('manager/products/get_products_by_category/', views.get_products_by_category, name='get_products_by_category'),

    # InStoreProduct list implementation
    path('manager/instoreproducts/', views.in_store_product_list, name='in_store_product_list'),
    path('manager/instoreproducts/addproduct', views.add_in_store_product, name='add_in_store_product'),
    path('manager/instoreproducts/edit/<int:id>/', views.edit_in_store_product_button, name='edit_in_store_product'),
    path('manager/instoreproducts/<int:id>/delete', views.delete_in_store_product, name='delete_in_store_product'),
    path('manager/instoreproducts/get_in_store_by_upc/', views.get_in_store_by_upc, name='get_in_store_by_upc'),

    # Check list implementation
    path('manager/checks/', views.check_list, name='check_list'),
    path('manager/checks/<int:id>/delete/', views.delete_check, name='delete_check'),
    path('manager/checks/watch/<int:id>/', views.watch_check, name='watch_check'),

    # Sales
    path('home/', views.home_page, name='home_page'),

]
