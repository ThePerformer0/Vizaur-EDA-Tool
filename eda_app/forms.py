from django import forms

class DatasetUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': '.csv,.xls,.xlsx',
            'class': 'file-input'
        })
    )