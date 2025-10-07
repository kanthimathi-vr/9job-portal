# app/forms.py
from django import forms

ROLE_CHOICES = (
    ('employee', 'Employee'),
    ('employer', 'Employer'),
)

class LoginForm(forms.Form):
    # Base input styling (border is handled in the template wrapper)
    INPUT_CLASS = "w-full px-4 py-3 bg-transparent focus:outline-none"

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Enter your username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASS,
            'placeholder': 'Enter your password'
        })
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-3 rounded-xl border border-gray-300 shadow-sm "
                     "focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 "
                     "text-gray-700 bg-white"
        }),
        label="Log in as",
        initial="employee"  # default selection, change to "employer" if you want
    )
