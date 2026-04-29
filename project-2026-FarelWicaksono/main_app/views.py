from django.shortcuts import render, redirect
from .models import Report
from .forms import ReportForm

# 1. Fungsi Home: Mengambil data dari database untuk ditampilkan
def home(request):
    # Mengambil semua data dari tabel Report dan diurutkan dari yang terbaru
    reports = Report.objects.all().order_by('-created_at') 
    return render(request, 'main_app/home.html', {'reports': reports})

# 2. Fungsi Add Report: Menangani input data dari form ke database
def add_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save() # Menyimpan data ke PostgreSQL
            return redirect('home') # Setelah simpan, balik ke halaman home
    else:
        form = ReportForm()
    
    return render(request, 'main_app/add_report.html', {'form': form})