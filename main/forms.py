from django import forms


class SearchBoozicornForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                   'class': 'form-control',
                   'placeholder': "Name a wine or spirit",
                   'name': 'Search button for boozicorns'
            }
        )
    )
