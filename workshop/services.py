from django.db import transaction
from django.db.models import F, Sum
from .models import Item, Transaction

class InventoryService:
    
    @staticmethod
    def get_dashboard_stats():
        """Логика для 1-й страницы (Dashboard)"""
        # Считаем общую стоимость всех материалов и товаров на складе
        total_value = Item.objects.aggregate(
            total=Sum(F('quantity') * F('price_buy'))
        )['total'] or 0
        
        # Находим позиции, которые заканчиваются (ниже мин. порога)
        low_stock_items = Item.objects.filter(quantity__lte=F('min_limit'))
        
        # Последние 5 операций для ленты активности
        recent_transactions = Transaction.objects.select_related('item').order_by('-date')[:5]
        
        return {
            'total_value': total_value,
            'low_stock_items': low_stock_items,
            'recent_transactions': recent_transactions,
        }

    @staticmethod
    @transaction.atomic
    def record_transaction(item_id, qty, t_type, user, contractor_id=None, comment=""):
        """
        Универсальный метод для страниц: Закупка, Продажа и Списание.
        Обновляет остатки и создает запись в истории.
        """
        item = Item.objects.select_for_update().get(id=item_id)
        
        # Логика изменения остатков
        if t_type in ['INBOUND', 'PROD_IN']:
            item.quantity += qty
        elif t_type in ['OUTBOUND', 'PROD_OUT']:
            if item.quantity < qty:
                raise ValueError(f"Недостаточно количества на складе ({item.name})")
            item.quantity -= qty
            
        item.save()
        
        # Создаем запись об операции
        return Transaction.objects.create(
            item=item,
            type=t_type,
            quantity=qty,
            employee=user,
            contractor_id=contractor_id,
            comment=comment
        )

    @staticmethod
    @transaction.atomic
    def produce_item(material_id, material_qty, product_id, product_qty, user):
        """
        Специальный метод для 4-й страницы (Производство).
        Списывает материалы и сразу создает готовую продукцию.
        """
        # 1. Списываем материалы (PROD_OUT)
        InventoryService.record_transaction(
            item_id=material_id,
            qty=material_qty,
            t_type='PROD_OUT',
            user=user,
            comment="Списание на производство"
        )
        
        # 2. Оприходуем готовое изделие (PROD_IN)
        InventoryService.record_transaction(
            item_id=product_id,
            qty=product_qty,
            t_type='PROD_IN',
            user=user,
            comment="Выпуск готовой продукции"
        )