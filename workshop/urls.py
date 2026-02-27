from django.urls import path
from . import views

urlpatterns = [
    # 1. Главная (Dashboard)
    path('', views.dashboard, name='dashboard'),
    
    # 2. Склад (Inventory)
    path('inventory/', views.inventory_list, name='inventory_list'),
    
    # 3. Закупка (Purchase)
    path('purchase/', views.purchase_create, name='purchase_create'),
    
    # 4. Производство (Production)
    path('production/', views.production_create, name='production_create'),
    
    # 5. Партнеры (Partners)
    path('partners/', views.partners_list, name='partners_list'),
    
    # 6. Журнал операций (History)
    path('history/', views.history_list, name='history_list'),
    path('sales/', views.sales_create, name='sales_create'),
]