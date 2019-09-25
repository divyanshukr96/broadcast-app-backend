from abc import ABC

from django.contrib.auth import authenticate
from requests import request
from rest_framework import serializers
from Users.models import User, Faculty, Student


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ('user_type',)
        fields = ('id', 'name', 'email', 'mobile', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'mobile', 'username', 'password', 'user_type')
        # fields = "__all__"

        # exclude = ('last_login', 'is_superuser', 'is_staff', 'date_joined',)


class FacultySerializers(serializers.ModelSerializer):
    user = UserSerializers()
    user_type = serializers.ChoiceField(choices=['Faculty'])

    class Meta:
        model = Faculty
        fields = ('user', 'user_type', 'department', 'designation', 'sex', 'dob',)


class StudentSerializers(serializers.ModelSerializer):
    user = UserSerializers()

    class Meta:
        model = Student
        fields = ('user', 'department', 'registration_number', 'batch', 'program', 'sex', 'dob')
        # fields = ('department', 'registration_number', 'batch', 'program', 'sex', 'dob')


class RegisterSerializers(serializers.ModelSerializer):
    department = serializers.ChoiceField(choices=User.objects.filter(user_type="DEPARTMENT"))
    registration_number = serializers.CharField()
    batch = serializers.IntegerField()
    program = serializers.CharField()
    sex = serializers.ChoiceField(choices=['MALE', 'FEMALE', 'OTHER'])
    dob = serializers.DateField()

    class Meta:
        model = User
        fields = (
            'name', 'email', 'mobile', 'username', 'password', 'user_type',
            'department', 'registration_number', 'batch', 'program', 'sex', 'dob',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'name': {'required': True},
            'email': {'required': True, },
            'mobile': {'required': True, },
            'user_type': {'required': True, }
        }

    def to_representation(self, instance):
        print(instance)
        return instance

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user_data = {
            "name": validated_data.pop('name'),
            "mobile": validated_data.pop('mobile'),
            'user_type': validated_data.pop('user_type')
        }
        # print(validated_data)
        user = User.objects.create_user(username=username, email=email, password=password, **user_data)
        student = Student.objects.create(user=user, **validated_data)
        return user


class UserDetailSerializers(serializers.ModelSerializer):
    student = StudentSerializers(read_only=True)
    faculty = FacultySerializers(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'mobile', 'username', 'user_type', 'is_admin', 'student', 'faculty')


class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect credentials", 422)


class PublicDepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')
