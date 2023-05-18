from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100, required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'Enter your email', 'onfocus': 'animateButton("#47AB11")'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter your password', 'onfocus': 'animateButton("#47AB11")'}), required=True)


class EmployeeForm(forms.Form):
    surname = forms.CharField(max_length=100)
    name = forms.CharField(max_length=100)
    patronymic = forms.CharField(max_length=100, required=False)
    role = forms.CharField(max_length=100)
    salary = forms.DecimalField(max_digits=10, decimal_places=4)
    date_of_birth = forms.DateField()
    date_of_start = forms.DateField()
    phone_number = forms.CharField(max_length=20)
    city = forms.CharField(max_length=100)
    street = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class EditEmployeeForm(forms.Form):
    surname = forms.CharField(max_length=100, required=False)
    name = forms.CharField(max_length=100, required=False)
    patronymic = forms.CharField(max_length=100, required=False)
    role = forms.CharField(max_length=100, required=False)
    salary = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    date_of_birth = forms.DateField(required=False)
    date_of_start = forms.DateField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False)
    street = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

class CustomerForm(forms.Form):
    surname = forms.CharField(max_length=100)
    name = forms.CharField(max_length=100)
    patronymic = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=20)
    city = forms.CharField(max_length=100, required=False)
    street = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    percent = forms.CharField(max_length=5)

class EditCustomerForm(forms.Form):
    surname = forms.CharField(max_length=100, required=False)
    name = forms.CharField(max_length=100, required=False)
    patronymic = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False)
    street = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    percent = forms.CharField(max_length=5, required=False)
