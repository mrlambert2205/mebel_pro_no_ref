from django.db import models
from django.contrib.auth.models import User

# 1. Категории (страница Склад / Настройки)
class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

# 2. Номенклатура: и материалы, и готовая мебель (страница Склад)
class Item(models.Model):
    TYPES = [
        ('MATERIAL', 'Материал/Сырье'),
        ('PRODUCT', 'Готовая продукция'),
    ]
    
    name = models.CharField("Наименование", max_length=200)
    sku = models.CharField("Артикул/Код", max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    item_type = models.CharField("Тип", max_length=10, choices=TYPES, default='MATERIAL')
    
    quantity = models.DecimalField("Остаток на складе", max_digits=10, decimal_places=2, default=0)
    unit = models.CharField("Ед. измерения", max_length=10, default="шт.") # м3, пог. м, шт.
    
    price_buy = models.DecimalField("Цена закупки", max_digits=10, decimal_places=2, default=0)
    price_sale = models.DecimalField("Цена продажи", max_digits=10, decimal_places=2, default=0)
    
    min_limit = models.DecimalField("Мин. запас", max_digits=10, decimal_places=2, default=5)

    class Meta:
        verbose_name = "Объект склада"
        verbose_name_plural = "Склад"

    def __str__(self):
        return f"{self.name} ({self.sku})"

# 3. Поставщики и Покупатели (страница Партнеры)
class Contractor(models.Model):
    TYPE_CHOICES = [
        ('SUPPLIER', 'Поставщик материала'),
        ('CUSTOMER', 'Покупатель мебели'),
    ]
    name = models.CharField("Название/ФИО", max_length=200)
    contractor_type = models.CharField("Тип партнера", max_length=10, choices=TYPE_CHOICES)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"

    def __str__(self):
        return self.name

# 4. Движение товаров (страницы Закупка, Производство, Отгрузка, История)
class Transaction(models.Model):
    TRAN_TYPES = [
        ('INBOUND', 'Закупка (Приход)'),
        ('OUTBOUND', 'Продажа (Расход)'),
        ('PROD_IN', 'Производство (Выпуск готовой мебели)'),
        ('PROD_OUT', 'Производство (Списание материалов)'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Товар/Материал")
    type = models.CharField("Тип операции", max_length=10, choices=TRAN_TYPES)
    quantity = models.DecimalField("Количество", max_digits=10, decimal_places=2)
    
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Партнер")
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Сотрудник")
    
    date = models.DateTimeField("Дата и время", auto_now_add=True)
    comment = models.TextField("Комментарий", blank=True)

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "История операций"

    def __str__(self):
        return f"{self.date.strftime('%d.%m %H:%M')} | {self.get_type_display()} | {self.item.name}"