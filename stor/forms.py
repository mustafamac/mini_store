from django import forms
from .models import CustomerInfo

class CustomerInfoForm(forms.ModelForm):
    class Meta:
        model = CustomerInfo
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'zip_code', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الكامل'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'العنوان', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المدينة'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الرمز البريدي'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ملاحظات إضافية', 'rows': 2}),
        }