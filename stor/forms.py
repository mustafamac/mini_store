from django import forms
from .models import CustomerInfo

class CustomerInfoForm(forms.ModelForm):
    class Meta:
        model = CustomerInfo
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم ثلاثي', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01xxxxxxxxx', 'required': 'required'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'اسم الشارع، رقم العمارة، الشقة...', 'rows': 2, 'required': 'required'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'القاهرة، الإسكندرية...', 'required': 'required'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'أي ملاحظات إضافية بخصوص التسليم', 'rows': 2}),
        }