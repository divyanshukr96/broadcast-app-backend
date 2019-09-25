from rest_framework import viewsets, permissions, generics
from Notice import permissions as notice_permission
from Notice.models import Notice
from .serializers import NoticeSerializers, PublicNoticeSerializers


class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializers
    queryset = Notice.objects.all()

    permission_classes = [
        permissions.IsAuthenticated,
        notice_permission.IsNoticeUser,
    ]

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user'] = self.request.user
        notice = serializer.save()

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

    def get_queryset(self):
        queryset = self.model.objects.filter(public_notice=True)
        return queryset

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

        queryset = self.model.objects.filter(public_notice=False)

        if user.user_type == "STUDENT":
            queryset = queryset.filter(department=user.student_user.department)
        elif user.user_type == "DEPARTMENT":
            print('sds')
        elif user.user_type == "SOCIETY":
            queryset = queryset.filter(department=user.society_user.department)
        elif user.user_type == "FACULTY":
            queryset = queryset.filter(department=user.faculty_user.department)
        else:
            pass

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
