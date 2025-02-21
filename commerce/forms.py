from django import forms
from phonenumber_field.modelfields import PhoneNumberField

from commerce.models import *


class CommentModelForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name','rating', 'email','content']


class CustomerModelForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'email','description','vat_number', 'address', 'phone_number']

class ProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'rating', 'price', 'discount', 'quantity', 'shipping_cost', 'model', 'tags', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()