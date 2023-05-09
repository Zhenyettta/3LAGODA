from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100, required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'Enter your email', 'onfocus': 'animateButton("#47AB11")'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter your password', 'onfocus': 'animateButton("#47AB11")'}), required=True)
