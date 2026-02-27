from django.contrib import admin
from django.urls import path, include # Не забудь импортировать include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('workshop.urls')), # Подключаем наше приложение к корню сайта
]