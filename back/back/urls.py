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
    path('home/',views.home_page, name='home_page'),
    # Manager
    path('manager/', views.manager_page, name='manager_page'),

    # Employee list manipulations
    path('manager/employees/', views.empl_list, name='empl_list'),
    path('manager/addemployee/', views.add_employee, name='add_employee'),
    path('manager/employees/edit/<int:id>/', views.edit_employee_button, name='edit_employee'),
    path('manager/employees/<int:id>/delete/', views.delete_employee, name='delete_employee'),
    path('manager/employees/onlysales/', views.empl_only_sales_list, name='empl_only_sales_list'),

    # Customer list implementation
    path('manager/customers/', views.cust_list, name='cust_list'),

    # Category list implementation
    path('manager/categories/', views.category_list, name='category_list'),

    # Product list implementation
    path('manager/product/', views.product_list, name='product_list'),

    # InStoreProduct list implementation
    path('manager/instoreproduct/', views.in_store_product_list, name='in_store_product_list'),
]
