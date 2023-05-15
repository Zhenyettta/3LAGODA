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
    patronymic = forms.CharField(max_length=100,required=False)
    role = forms.CharField(max_length=100)
    salary = forms.DecimalField(max_digits=10, decimal_places=2)
    date_of_birth = forms.DateField()
    date_of_start = forms.DateField()
    phone_number = forms.CharField(max_length=20)
    city = forms.CharField(max_length=100)
    street = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())