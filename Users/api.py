from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from Users.models import User, Faculty, Student
from rest_framework import viewsets, permissions, generics

from Users.serializers import RegisterSerializers, UserDetailSerializers, UserSerializers, ChannelSerializers
from Users.serializers import LoginSerializers, PasswordSerializers
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
            'registration_number': request.data['registration_number'],
            'program': request.data['program'],
            'batch': request.data['batch'],
            'sex': request.data['sex'],
            'dob': request.data['dob'],
        }
        return Response(data_send)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
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
    queryset = User.objects.filter(user_type__in=['DEPARTMENT', 'SOCIETY']).order_by('user_type', '-is_admin')
