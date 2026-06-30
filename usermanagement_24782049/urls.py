from django.urls import path
from .views import CitizenLoginView, CitizenLogoutView, CitizenRegisterView

urlpatterns = [
    path('login/', CitizenLoginView.as_view(), name='login'),
    path('logout/', CitizenLogoutView.as_view(), name='logout'),
    path('register/', CitizenRegisterView.as_view(), name='register'),
]