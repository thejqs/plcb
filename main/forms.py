from django import forms
from django.forms import ModelForm
# import datetime
from main.models import Unicorns, Stores

# today = datetime.date.today()


class SearchBoozicornForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "Whatcha lookin' for?",
            }
        )
    )
