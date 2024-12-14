# blog/views/pages_view.py
from django.shortcuts import render
from django.http import HttpResponse

def homepage(request):
    # Add any logic for the homepage if necessary
    return render(request, 'blog/pages/homepage.html')

def about(request):
    # Add any logic for the about page if necessary
    return render(request, 'blog/pages/about.html')

def contact(request):
    # Add any logic for the contact page if necessary
    return render(request, 'blog/pages/contact.html')
