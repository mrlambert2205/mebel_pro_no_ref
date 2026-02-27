from django import forms
from .models import Item, Category, Contractor, Transaction

# Базовый класс для стилизации всех форм под Bootstrap
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# 1. Форма для добавления нового товара или материала
class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'sku', 'category', 'item_type', 'unit', 'price_buy', 'price_sale', 'min_limit']

# 2. Форма для закупки или продажи (Транзакции)
class TransactionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['item', 'quantity', 'contractor', 'comment']
    
    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty <= 0:
            raise forms.ValidationError("Количество должно быть больше нуля")
        return qty

# 3. Форма для производства (Страница №4)
# Это не ModelForm, так как она объединяет действия над двумя объектами
class ProductionForm(BootstrapFormMixin, forms.Form):
    material = forms.ModelChoiceField(
        queryset=Item.objects.filter(item_type='MATERIAL'),
        label="Расходный материал (сырье)"
    )
    material_quantity = forms.DecimalField(label="Сколько списать материала", min_value=0.1)
    
    product = forms.ModelChoiceField(
        queryset=Item.objects.filter(item_type='PRODUCT'),
        label="Результат (готовая мебель)"
    )
    product_quantity = forms.DecimalField(label="Сколько произведено", min_value=1)

# 4. Форма для партнеров
class ContractorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ['name', 'contractor_type', 'phone', 'email']