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


@api_view(['POST'])
def faculty(request):
    if not request.user.is_authenticated:
        return Response("Unauthenticated", 401)
    import io
    import csv
    from Users.models import User, Faculty, FACULTY
    from django.contrib.auth.hashers import make_password
    csv_files = request.FILES.get('file')

    if not csv_files or not csv_files.name.endswith('.csv'):
        return Response('file error', 400)

    data_set = csv_files.read().decode('UTF-8')

    io_string = io.StringIO(data_set)
    # next(data_set)

    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        try:
            if not column[2]:
                continue
            fac, created = User.objects.get_or_create(
                name=column[1],
                email=column[2],
                password=make_password(column[3]),
                user_type=FACULTY
            )
            if created:
                Faculty.objects.create(user=fac, department_id=column[4], designation=column[5])
        except:
            pass

    return Response()
