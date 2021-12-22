from django import forms


class UserForm(forms.Form):
    name = forms.CharField(label='用户账号', max_length=50)
    password = forms.CharField(label='密码', max_length=50, widget=forms.PasswordInput)