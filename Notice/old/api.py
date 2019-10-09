from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from Notice import permissions as notice_permission
from Notice.models import Notice
from .serializers import NoticeSerializers, PublicNoticeSerializers


class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializers
    queryset = Notice.objects.all()

    parser_classes = [JSONParser, FormParser, MultiPartParser]

    permission_classes = [
        permissions.IsAuthenticated,
        notice_permission.IsNoticeUser,
    ]

    def perform_create(self, serializer):
        temp_dept = self.request.POST.getlist('department[]')
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user'] = self.request.user
        if temp_dept.__len__() >= 1:
            serializer.validated_data['department'] = temp_dept
        # serializer.validated_data['department'] =
        notice = serializer.save()
        # print(notice)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class PublicNoticeAPI(generics.ListAPIView):
    serializer_class = PublicNoticeSerializers

    model = serializer_class.Meta.model

    queryset = Notice.objects.all()

    permission_classes = [
        permissions.AllowAny
    ]

    # def get_queryset(self):
    #     queryset = self.model.objects.filter(public_notice=True)
    #     return queryset

    # user = self.request.user
    # queryset = self.model.objects
    # if user.is_authenticated and user.user_type != "STUDENT":
    #     queryset = queryset.filter(public_notice=False)
    # return queryset.order_by('-title')


class PrivateNoticeAPI(generics.ListAPIView):
    serializer_class = PublicNoticeSerializers

    model = serializer_class.Meta.model

    queryset = Notice.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == "STUDENT":
            queryset = self.model.objects.filter(public_notice=True)
            queryset = queryset.filter(department=user.student_user.department)
        elif user.user_type == "DEPARTMENT":
            queryset = self.model.objects.all()
            queryset = queryset.filter(user=user)
        elif user.user_type == "SOCIETY":
            queryset = self.model.objects.all()
            queryset = queryset.filter(user=user)
        elif user.user_type == "CHANNEL":
            queryset = self.model.objects.all()
            queryset = queryset.filter(user=user)
        elif user.user_type == "FACULTY":
            queryset = self.model.objects.filter(public_notice=False)
            queryset = queryset.filter(department=user.faculty_user.department)
        else:
            queryset = self.model.objects.filter(public_notice=False)

        # queryset = queryset.filter(department=user.faculty_user.department)
        # if user.user_type in ["STUDENT", "SOCIETY"]:
        #     queryset = queryset.filter(department=user.faculty_user.department)

        # print(queryset.get().user)
        return queryset

        # user = self.request.user
        # queryset = self.model.objects
        # if user.is_authenticated and user.user_type != "STUDENT":
        #     queryset = queryset.filter(public_notice=False)
        # return queryset.order_by('-title')
