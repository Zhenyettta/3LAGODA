from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100, required=True,
                             widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}), required=True)
