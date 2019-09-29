from django.shortcuts import render

# Create your views here.
from rest_framework.exceptions import NotFound


def error404(request):
    raise NotFound(detail="Error 404, page not found", code=404)


def homeview(request):
    return render(request, "privacy_policy.html")


def coming(request):
    return render(request, "coming_soon.html")
