from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Item, Transaction, Contractor
from .services import InventoryService
from .forms import ItemForm, TransactionForm, ProductionForm, ContractorForm

# 1. Dashboard (Главная — «Пульс бизнеса»)
def dashboard(request):
    # Получаем всю аналитику из сервиса одной командой
    stats = InventoryService.get_dashboard_stats()
    return render(request, 'workshop/dashboard.html', stats)

# 2. Inventory (Склад — «Каталог»)
def inventory_list(request):
    items = Item.objects.all().select_related('category')
    return render(request, 'workshop/inventory.html', {'items': items})

# 3. Inbound (Закупка — «Приемка материалов»)
def purchase_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            InventoryService.record_transaction(
                item_id=data['item'].id,
                qty=data['quantity'],
                t_type='INBOUND',
                user=request.user,
                contractor_id=data['contractor'].id if data['contractor'] else None,
                comment=data['comment']
            )
            messages.success(request, "Материалы успешно приняты на склад")
            return redirect('history_list')
    else:
        form = TransactionForm()
    return render(request, 'workshop/transaction_form.html', {
        'form': form, 
        'title': 'Закупка материалов (Приход)'
    })

# 4. Production (Производство — «Цех»)
# Здесь мы используем специальный метод сервиса для превращения материалов в мебель
def production_create(request):
    if request.method == 'POST':
        form = ProductionForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                InventoryService.produce_item(
                    material_id=data['material'].id,
                    material_qty=data['material_quantity'],
                    product_id=data['product'].id,
                    product_qty=data['product_quantity'],
                    user=request.user
                )
                messages.success(request, "Производство завершено: материал списан, мебель добавлена")
                return redirect('inventory_list')
            except ValueError as e:
                messages.error(request, str(e)) # Если не хватило досок
    else:
        form = ProductionForm()
    return render(request, 'workshop/production_form.html', {'form': form})

# 5. Partners (Контрагенты — «Контакты»)
def partners_list(request):
    contractors = Contractor.objects.all()
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('partners_list')
    else:
        form = ContractorForm()
    return render(request, 'workshop/partners.html', {
        'contractors': contractors, 
        'form': form
    })

# 6. History (Журнал операций — «Аудит»)
def history_list(request):
    transactions = Transaction.objects.all().select_related(
        'item', 'employee', 'contractor'
    ).order_by('-date')
    return render(request, 'workshop/history.html', {'transactions': transactions})

def sales_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                # Проверяем, что продаем именно ПРОДУКТ, а не доски
                if data['item'].item_type != 'PRODUCT':
                    messages.error(request, "Для продажи выберите готовую продукцию, а не материалы.")
                else:
                    InventoryService.record_transaction(
                        item_id=data['item'].id,
                        qty=data['quantity'],
                        t_type='OUTBOUND', # Тип: Расход/Продажа
                        user=request.user,
                        contractor_id=data['contractor'].id if data['contractor'] else None,
                        comment=f"Продажа клиенту: {data['comment']}"
                    )
                    messages.success(request, f"Товар {data['item'].name} успешно отгружен клиенту")
                    return redirect('inventory_list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        # Показываем в списке выбора только Готовую продукцию
        form = TransactionForm()
        form.fields['item'].queryset = Item.objects.filter(item_type='PRODUCT')
        
    return render(request, 'workshop/transaction_form.html', {
        'form': form,
        'title': 'Оформление продажи (Отгрузка)'
    })