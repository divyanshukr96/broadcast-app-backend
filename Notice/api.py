from rest_framework import viewsets, permissions

from Notice.models import Notice
from .serializers import NoticeSerializers


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = NoticeSerializers


