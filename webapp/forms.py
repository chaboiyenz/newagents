from django import forms
from .models import *

class ProvinceForm(forms.ModelForm):
    class Meta:
        model = Province
        fields = ['name']

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['province', 'name']

class SubdivisionForm(forms.ModelForm):
    class Meta:
        model = Subdivision
        fields = [
            'name', 'description', 'commission', 'price_min', 'price_max',
            'messenger_link', 'google_drive_link', 'construction_status',
            'developer', 'city', 'priority', 'image1', 'image2', 'image3', 'image4',
            'location', 'house_model'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter subdivision name'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe this subdivision', 
                'rows': 4,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'messenger_link': forms.URLInput(attrs={'placeholder': 'https://'}),
            'google_drive_link': forms.URLInput(attrs={'placeholder': 'https://'}),
            'construction_status': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'}),
            'developer': forms.TextInput(attrs={'placeholder': 'Enter developer name'}),
            'price_min': forms.NumberInput(attrs={'placeholder': '₱', 'min': 0}),
            'price_max': forms.NumberInput(attrs={'placeholder': '₱', 'min': 0}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location details'}),
            'house_model': forms.TextInput(attrs={'placeholder': 'Enter house model description'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make certain fields optional
        optional_fields = [
            'messenger_link', 'google_drive_link', 'construction_status',
            'developer', 'image1', 'image2', 'image3', 'image4',
            'location', 'house_model'
        ]
        for field in optional_fields:
            self.fields[field].required = False
        
        # Set common input styles for all fields
        input_classes = 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
        
        for field_name, field in self.fields.items():
            if field_name != 'description':  # We already set custom attrs for description in Meta
                field.widget.attrs.update({'class': input_classes})
            
            # Add specific styling/attrs for certain fields
            if 'image' in field_name:
                field.widget.attrs.update({
                    'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                    'accept': 'image/*'
                })
            elif field_name in ['messenger_link', 'google_drive_link']:
                field.widget.attrs['class'] = 'flex-1 block w-full px-4 py-3 rounded-r-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'

    def clean(self):
        cleaned_data = super().clean()
        price_min = cleaned_data.get('price_min')
        price_max = cleaned_data.get('price_max')
        
        # Validate that price_max is greater than price_min
        if price_min is not None and price_max is not None and price_min > price_max:
            self.add_error('price_max', "Maximum price must be greater than minimum price.")
        
        return cleaned_data
        
    def clean_messenger_link(self):
        url = self.cleaned_data.get('messenger_link')
        if url and not (url.startswith('http://') or url.startswith('https://')):
            return f'https://{url}'
        return url

    def clean_google_drive_link(self):
        url = self.cleaned_data.get('google_drive_link')
        if url and not (url.startswith('http://') or url.startswith('https://')):
            return f'https://{url}'
        return url

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['title', 'file', 'description', 'when', 'where']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'file': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'when': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2 border rounded'}),
            'where': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

    