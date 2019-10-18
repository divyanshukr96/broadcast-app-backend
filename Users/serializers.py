from django.contrib.auth import authenticate, get_user_model
from django.core.validators import validate_email as validate_email_address
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.utils import json

from Users.models import User, Faculty, Student, Follower

PROGRAM_CHOICE = [
    ('ICD', 'Integrated Certificate Diploma'),
    ('BE', 'Bachelor of Engineering'),
    ('MTech', 'Master of Technology'),
    ('MBA', 'Master of Business Administration'),
    ('MSc ', 'Master of Science'),
    ('PhD', 'Doctor of Philosophy'),
]


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
        fields = ('user', 'user_type', 'department', 'designation', 'gender', 'dob',)


class StudentSerializers(serializers.ModelSerializer):
    user = UserSerializers()
    department = serializers.SerializerMethodField('get_department')

    class Meta:
        model = Student
        fields = ('user', 'department', 'registration_number', 'batch', 'program', 'gender', 'dob')
        # fields = ('department', 'registration_number', 'batch', 'program', 'gender', 'dob')

    @staticmethod
    def get_department(student):
        if student.department:
            return student.department.name
        return


class RegisterSerializers(serializers.ModelSerializer):
    try:
        department = serializers.ChoiceField(choices=User.objects.filter(user_type="DEPARTMENT", is_admin=False))
    except:
        pass
    registration_number = serializers.IntegerField()
    batch = serializers.IntegerField(min_value=now().year - 9, max_value=now().year)
    program = serializers.ChoiceField(choices=PROGRAM_CHOICE)
    gender = serializers.ChoiceField(choices=['MALE', 'FEMALE', 'OTHER'])
    dob = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = (
            'name', 'email', 'mobile', 'username', 'password',
            'department', 'registration_number', 'batch', 'program', 'gender', 'dob',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'name': {'required': True},
            'email': {'required': True, },
            'mobile': {'required': True, },
            # 'user_type': {'required': True, }
        }

    def to_representation(self, instance):
        print(instance)
        return instance

    def validate_registration_number(self, value):
        program = self.initial_data.get('program')
        batch = self.initial_data.get('batch')
        if program == 'PhD' and len(str(value)) != 4:
            raise serializers.ValidationError("Invalid registration number.")
        elif len(str(value)) != 7:
            raise serializers.ValidationError("Invalid registration number.")

        if program == 'BE':
            if str(value)[:2] != batch[2:] and (str(value)[:3] != str(int(batch[2:]) + 1) + '3'):
                raise serializers.ValidationError("Invalid registration number.")
            elif str(value)[:2] == batch[2:] and (str(value)[:3] != str(batch[2:]) + '4'):
                raise serializers.ValidationError("Invalid registration number.")

        elif str(value)[:2] != batch[2:]:
            raise serializers.ValidationError("Invalid registration number.")
        if Student.objects.filter(registration_number=value).exists():
            raise serializers.ValidationError("Registration number already registered.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user_data = {
            "name": validated_data.pop('name'),
            "mobile": validated_data.pop('mobile'),
            'user_type': "STUDENT",
            'is_active': False,
        }
        # print(validated_data)
        user = User.objects.create_user(username=username, email=email, password=password, **user_data)
        student = Student.objects.create(user=user, **validated_data)
        print(user)
        return user


class FacultyRegisterSerializers(serializers.ModelSerializer):
    designation = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    mobile = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=['MALE', 'FEMALE', 'OTHER'])
    dob = serializers.DateField(required=False)

    class Meta:
        model = User

        fields = ('name', 'email', 'mobile', 'username', 'password', 'designation', 'gender', 'dob')

        extra_kwargs = {
            'password': {'write_only': True},
            'name': {'required': True},
            'email': {'required': True, },
            'mobile': {'required': True, },
            # 'user_type': {'required': True, }
        }

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        user_data = {
            "name": validated_data.pop('name'),
            "mobile": validated_data.pop('mobile'),
            'user_type': "FACULTY",
            'is_active': True,
        }
        print(validated_data)
        user = get_user_model().objects.get(email=email)
        user.name = user_data.get('name')
        user.username = username
        user.mobile = user_data.get('mobile')
        user.faculty_user.designation = validated_data.pop('designation')
        user.faculty_user.dob = validated_data.pop('dob')
        user.faculty_user.gender = validated_data.pop('gender')
        user.save()
        user.faculty_user.save()
        return user

    @staticmethod
    def validate_email(value):

        try:
            validate_email_address(value)
        except:
            raise serializers.ValidationError("Invalid email entered.")

        try:
            user = get_user_model().objects.get(email=value)
        except:
            raise serializers.ValidationError("This email is not registered.")

        try:
            user = get_user_model().objects.get(email=value)
            if user.username:
                raise
        except:
            raise serializers.ValidationError("This email is already registered.")

        return value

    def validate_mobile(self, value):
        email = self.initial_data.get('email')
        user = ""
        try:
            user = get_user_model().objects.get(mobile=value)
        except:
            return value

        if user.email == email:
            return value
        raise serializers.ValidationError("A user with that mobile already exists.")

    def validate_password(self, value):
        email = self.initial_data.get('email')
        user = ""
        try:
            validate_email_address(email)
            user = get_user_model().objects.get(email=email)
        except:
            pass

        if user and not user.check_password(value):
            raise serializers.ValidationError("Incorrect password entered.")
        return value


class UserDetailSerializers(serializers.ModelSerializer):
    student = StudentSerializers(read_only=True)
    faculty = FacultySerializers(read_only=True)
    details = serializers.SerializerMethodField('user_details')

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'mobile', 'username', 'user_type', 'is_admin', 'about', 'extra_fields', 'profile',
            'student', 'faculty', 'details')

    @staticmethod
    def user_details(user):
        if user.user_type == "STUDENT":
            return StudentSerializers(user.student_user).data
        return


class PasswordSerializers(serializers.ModelSerializer):
    password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('password', 'new_password')

    def validate(self, attrs):
        password = attrs.get('password')
        new_password = attrs.get('new_password')
        user = self.context.get('request').user
        if user.check_password(password):
            if user and user.is_active:
                return user
        raise serializers.ValidationError({
            'password': "Incorrect password"
        }, 422)


class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        try:
            validate_email_address(attrs.get('username'))
            temp_user = get_user_model().objects.get(email=attrs.get('username'))
            if temp_user.check_password(attrs.get('password')):
                if temp_user.username:
                    attrs['username'] = temp_user.username
                elif temp_user.user_type == "FACULTY":
                    return temp_user
        except:
            pass
        user = authenticate(**attrs)
        if user and user.is_active:
            return user
        raise serializers.ValidationError({
            'error': "Incorrect credentials"
        }, 422)


class PublicDepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'name')


class ChannelSerializers(serializers.ModelSerializer):
    following = serializers.SerializerMethodField('is_following')
    auth = serializers.SerializerMethodField('user_auth')
    is_admin = serializers.SerializerMethodField('admin_or_not')

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'profile', 'user_type', 'is_admin', 'following', 'auth')

    def is_following(self, channel):
        user = self._context["request"].user
        if user.is_authenticated:
            if user.user_type == "STUDENT" and channel == user.student_user.department:
                return True
            if user.user_type == "FACULTY" and channel == user.faculty_user.department:
                return True
            return Follower.is_following(channel=channel, user=user)
        return False

    def admin_or_not(self, channel):
        user = self._context["request"].user
        if user.is_authenticated:
            if user.user_type == "STUDENT" and channel == user.student_user.department:
                return True
            if user.user_type == "FACULTY" and channel == user.faculty_user.department:
                return True
        return channel.is_admin

    def user_auth(self, channel):
        user = self._context["request"].user
        if user:
            return user.is_authenticated
        return False


class FollowerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ('id',)
