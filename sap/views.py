from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'sap/home.html')

def dashboard(request):
    return render(request, 'sap/dashboard.html')