from django.contrib import admin # <-- Pastikan modul admin ini diimpor
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls), # <-- Tambahkan rute admin bawaan Django di sini
    path('', include('main_app.urls')),
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
]