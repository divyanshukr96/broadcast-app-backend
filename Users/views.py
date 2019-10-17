from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from Users.serializers import PROGRAM_CHOICE


def error404(request):
    raise NotFound(detail="Error 404, page not found", code=404)


def homeview(request):
    return render(request, "privacy_policy.html")


def coming(request):
    return render(request, "coming_soon.html")


@api_view(['GET'])
def program(request):
    return Response(PROGRAM_CHOICE, status=200)


@api_view(['GET'])
def app_version(request):
    return Response({
        'android': '1.2.0',
        'ios': '1.1.0'
    }, 200)
