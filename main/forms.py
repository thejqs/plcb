from django import forms
from django.forms import ModelForm
# import datetime
from main.models import Unicorn, Store

# today = datetime.date.today()


class SearchBoozicornForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "Name your booze",
                'name': 'Search button for boozicorns'
            }
        )
    )
