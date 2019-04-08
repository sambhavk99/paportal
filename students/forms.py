from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from .models import *
from .models import GroupRequest
from django import forms


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Reg. No. :',
        widget=forms.TextInput(attrs={'autofocus': True})
    )


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = CreateGroup
        fields = 'grp_name',


class RequestForm(forms.ModelForm):
    class Meta:
        model = GroupRequest
        fields = ('receiver',)


class StudentForm(forms.ModelForm):
    registration_no = forms.CharField(required=True)
    email = forms.EmailField(required=True, help_text="Required")

    class Meta:
        model = Student
        fields = ('registration_no', 'Name', 'FName', 'DOB', 'CPI', 'Category', 'Semester')


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ('pid', 'name', 'desg', 'aoi', 'group')


class DepartmentLoginForm(AuthenticationForm):
    username = UsernameField(
        label='Department username',
        widget=forms.TextInput(attrs={'autofocus': True}))
    department = forms.CharField(label='Department Name', required=True,
                                 help_text="Enter full department name, Ex - Computer Science and Engineering")

    class Meta:
        model = User
        fields = ('username', 'department', 'password')



