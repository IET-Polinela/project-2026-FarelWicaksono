from django.shortcuts import render

def about_view(request): # Nama fungsi ini bebas, tapi harus konsisten
    return render(request, 'about/about.html')