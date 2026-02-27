from django.contrib import admin
from .models import Category, Item, Contractor, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    # Что отображать в списке
    list_display = ('name', 'sku', 'category', 'item_type', 'quantity', 'unit', 'price_buy')
    # Фильтры справа
    list_filter = ('item_type', 'category')
    # Поиск по названию и артикулу
    search_fields = ('name', 'sku')

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contractor_type', 'phone')
    list_filter = ('contractor_type',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'type', 'item', 'quantity', 'employee')
    list_filter = ('type', 'date')
    # Запрещаем редактировать историю, чтобы нельзя было «подкрутить» остатки
    readonly_fields = ('date',)