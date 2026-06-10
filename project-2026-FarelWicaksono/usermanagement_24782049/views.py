from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import CitizenRegistrationForm

class CitizenLoginView(LoginView):
    template_name = 'usermanagement/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f"Selamat datang kembali, {form.get_user().username}! Berhasil login.")
        return super().form_valid(form)

class CitizenLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Anda telah berhasil logout dari sistem.")
        return super().dispatch(request, *args, **kwargs)

class CitizenRegisterView(CreateView):
    form_class = CitizenRegistrationForm
    template_name = 'usermanagement/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registrasi berhasil! Silakan login menggunakan akun Citizen Anda.")
        return super().form_valid(form)