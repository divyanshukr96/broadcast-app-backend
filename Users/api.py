from django.db.models import QuerySet, Q
from fcm_django.models import FCMDevice
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_206_PARTIAL_CONTENT

from Users.models import User, Faculty, Student, Follower
from rest_framework import viewsets, permissions, generics

from Users.serializers import RegisterSerializers, UserDetailSerializers, UserSerializers, ChannelSerializers, \
    FacultyRegisterSerializers, UserDetailWithNoticeSerializers
from Users.serializers import LoginSerializers, PasswordSerializers, FollowerSerializers
from .serializers import FacultySerializers, StudentSerializers, DepartmentSerializers, PublicDepartmentSerializers


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = FacultySerializers


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = StudentSerializers


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = DepartmentSerializers


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_data = UserSerializers(user, context=self.get_serializer_context()).data
        data_send = {
            **user_data,
            'department': request.data['department'],
            'registration_number': request.data.get('registration_number'),
            'program': request.data.get('program'),
            'batch': request.data.get('batch'),
            'gender': request.data.get('gender'),
            'dob': request.data.get('dob'),
        }
        return Response(data_send, status=201)


class FacultyRegisterAPI(generics.GenericAPIView):
    serializer_class = FacultyRegisterSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_data = UserSerializers(user, context=self.get_serializer_context()).data
        data_send = {
            **user_data,
            'department': request.data['department'],
            'designation': request.data['designation'],
            'gender': request.data['gender'],
            'dob': request.data['dob'],
        }
        return Response(data_send, status=201)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if not user.username:
            return Response({
                'email': user.email.lower(),
                'name': user.get_full_name(),
                'mobile': user.mobile,
                'department': user.faculty_user.department.name,
                'designation': user.faculty_user.designation,
                'gender': user.faculty_user.gender,
                'dob': user.faculty_user.dob
            }, status=HTTP_206_PARTIAL_CONTENT)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            **UserDetailSerializers(user, context=self.get_serializer_context()).data,
            'token': token.key
        }, status=HTTP_200_OK)


class UserAPI(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user


class UserUpdateAPI(generics.UpdateAPIView):
    serializer_class = UserDetailSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user


class PasswordUpdateAPI(generics.UpdateAPIView):
    serializer_class = PasswordSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if request.data.get('password') == request.data.get('new_password'):
            pass
        token = Token.objects.get(user=user)
        if user.check_password(request.data.get('password')):
            user.set_password(request.data.get('new_password'))
            user.save()
            if token:
                token.delete()
                token, _ = Token.objects.update_or_create(user=user)

            return Response({
                **UserDetailSerializers(user, context=self.get_serializer_context()).data,
                'token': token.key
            }, status=HTTP_200_OK)

        return Response({
            **UserDetailSerializers(user, context=self.get_serializer_context()).data,
        }, status=HTTP_200_OK)


class PublicDepartmentAPI(generics.ListAPIView):
    serializer_class = PublicDepartmentSerializers
    queryset = User.objects.filter(user_type="DEPARTMENT", is_admin=False)


class ChannelAPI(generics.ListAPIView):
    serializer_class = ChannelSerializers

    permission_classes = [
        permissions.AllowAny
    ]

    queryset = User.objects.filter(user_type__in=[
        'DEPARTMENT', 'SOCIETY', 'CHANNEL'
    ]).order_by('user_type', '-is_admin')

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
            params = self.request.query_params
            if params.get('admin'):
                queryset = queryset.filter(is_admin=params.get('admin') is not None)
            if params.get('type'):
                queryset = queryset.filter(user_type=params.get('type').upper(), is_admin=False)
        return queryset


class ChannelFollowingAPI(generics.ListAPIView):
    serializer_class = ChannelSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = User.objects.filter(user_type__in=[
        'DEPARTMENT', 'SOCIETY', 'CHANNEL'
    ], ).order_by('user_type', '-is_admin')

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
            user = self.request.user
            follow = [o.id for o in user.get_following()]
            if user.user_type == "STUDENT":
                queryset = queryset.filter(Q(id__in=follow) | Q(is_admin=True) | Q(id=user.student_user.department.id))
            elif user.user_type == "FACULTY":
                queryset = queryset.filter(Q(id__in=follow) | Q(is_admin=True) | Q(id=user.faculty_user.department.id))
            else:
                queryset = queryset.filter(Q(id__in=follow) | Q(is_admin=True))
        return queryset


class ChannelFollowAPI(viewsets.ModelViewSet):
    serializer_class = FollowerSerializers

    permission_classes = [
        permissions.IsAuthenticated
    ]

    queryset = Follower.objects.all()

    @staticmethod
    def __follow_change(request, status, *args, **kwargs):
        try:
            res_status = 200
            response = 'You are now following to '
            if not status:
                response = "You have un-follow the "
            if kwargs['pk']:
                to_user = User.objects.get(id=kwargs['pk'])
                request.user.add_follower(to=to_user, status=status)
                response += to_user.name
            return Response({
                response
            }, status=res_status)
        except:
            return Response({
                'following': 'Not found'
            }, status=400)

    def create(self, request, *args, **kwargs):
        return self.__follow_change(request, status=True, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return self.__follow_change(request, status=False, *args, **kwargs)

    #
    # def get_queryset(self):
    #     queryset = self.queryset
    #     if isinstance(queryset, QuerySet):
    #         queryset = queryset.all()
    #         params = self.request.query_params
    #         if params.get('type'):
    #             queryset = queryset.filter(user_type=params.get('type').upper())
    #     return queryset


class UserDetailWithNotice(viewsets.ModelViewSet):
    serializer_class = UserDetailWithNoticeSerializers

    queryset = User.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(user_type__in=['CHANNEL', 'DEPARTMENT', 'SOCIETY'])
        return queryset
