from rest_framework import viewsets, permissions

from Notice.models import Notice, Department
from .serializers import NoticeSerializers, DepartmentSerializers


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = NoticeSerializers


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = DepartmentSerializers
