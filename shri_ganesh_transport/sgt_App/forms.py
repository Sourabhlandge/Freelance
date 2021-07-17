from django import forms
from sgt_App.models import Entries
from django.forms.widgets import DateInput

class AddEntryForm(forms.ModelForm):
    class Meta:
        model = Entries
        fields = ['date','firm_name','lr_no','vehicle_no', 'location',
                    'amount', 'cash', 'diesel', 'rtgs', 'commission', 'status']
        widgets = {'date':DateInput(attrs={'type':'date'})}