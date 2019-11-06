from django.db.models import QuerySet, Q
from rest_framework import viewsets, permissions, generics, status, mixins
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Notice import permissions as notice_permission
from Notice.models import Notice, Image, Bookmark, NoticeView, Interested
from Notice.paginations import NoticePagination
from Users.models import User
from .serializers import NoticeSerializers, PublicNoticeSerializers, NoticeImageSerializers, NoticeViewsSerializers


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
        # if temp_dept.__len__() >= 1:
        #     data = User.objects.filter(user_type="DEPARTMENT", is_admin=False, id__in=temp_dept)
        #     serializer.validated_data['department'] = temp_dept
        # serializer.validated_data['department'] =
        notice = serializer.save()
        # print(notice)

    def perform_update(self, serializer):
        temp_dept = self.request.POST.getlist('department[]')
        serializer.is_valid(raise_exception=True)
        # if temp_dept.__len__() >= 1:
        #     serializer.validated_data['department'] = temp_dept
        serializer.save()

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class PublicNoticeAPI(generics.ListAPIView):
    serializer_class = PublicNoticeSerializers
    pagination_class = NoticePagination

    model = serializer_class.Meta.model

    queryset = Notice.objects.all()

    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        return self.queryset.filter(public_notice=True).order_by('-created_at')

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
    pagination_class = NoticePagination

    model = serializer_class.Meta.model

    queryset = Notice.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == "STUDENT":
            queryset = self.model.objects.filter(public_notice=True)
            queryset = queryset.filter(
                Q(user=user.student_user.department) | Q(user__is_admin=True) | Q(user__in=user.get_following()))
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
            queryset = queryset.filter(
                Q(user=user.faculty_user.department) | Q(user__is_admin=True) | Q(user__in=user.get_following()))
        else:
            queryset = self.model.objects.filter(public_notice=False)

        # queryset = queryset.filter(department=user.faculty_user.department)
        # if user.user_type in ["STUDENT", "SOCIETY"]:
        #     queryset = queryset.filter(department=user.faculty_user.department)

        # print(queryset.get().user)
        return queryset.order_by('-created_at')

        # user = self.request.user
        # queryset = self.model.objects
        # if user.is_authenticated and user.user_type != "STUDENT":
        #     queryset = queryset.filter(public_notice=False)
        # return queryset.order_by('-title')


class DeleteNoticeImage(generics.DestroyAPIView):
    serializer_class = NoticeImageSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        queryset = Image.objects.filter(id=self.kwargs['pk'], notice=self.kwargs['pk_notice'])
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.deleted_at:
            return Response("Cannot delete default system category", status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookmarkAPI(mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = PublicNoticeSerializers
    pagination_class = NoticePagination

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = Notice.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            notice = Notice.objects.get(id=kwargs.get('pk'))

            if kwargs.get('pk') and notice:
                message = "Bookmark added"
                bookmark, created = Bookmark.objects.get_or_create(user=request.user, notice=notice)
                if not created:
                    bookmark.delete()
                    message = "Bookmark removed"

                return Response({
                    "success": message
                }, 200)
        except:
            pass

        return Response('Notice not found', 404)

    def get_queryset(self):
        bookmark = Bookmark.objects.filter(user=self.request.user).values_list('notice_id', flat=True)
        queryset = self.queryset.filter(id__in=bookmark)

        return queryset.order_by('-created_at')


class InterestedAPI(mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = PublicNoticeSerializers

    pagination_class = NoticePagination

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = Notice.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            notice = Notice.objects.get(id=kwargs.get('pk'))

            if kwargs.get('pk') and notice:
                message = "You have marked yourself for this event"
                interested, created = Interested.objects.get_or_create(user=request.user, notice=notice)
                if not created:
                    interested.delete()
                    message = "Event unmarked"

                return Response({
                    "success": message
                }, 200)
        except:
            pass

        return Response('Notice not found', 404)

    def get_queryset(self):
        interested = Interested.objects.filter(user=self.request.user).values_list('notice_id', flat=True)
        queryset = self.queryset.filter(id__in=interested)

        return queryset.order_by('-created_at')


class NoticeViewsViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = NoticeViewsSerializers
    queryset = NoticeView.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, args, kwargs)
