from django.contrib.auth import authenticate
from django.utils.timezone import now
from rest_framework import serializers
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

    class Meta:
        model = Student
        fields = ('user', 'department', 'registration_number', 'batch', 'program', 'gender', 'dob')
        # fields = ('department', 'registration_number', 'batch', 'program', 'gender', 'dob')


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


class UserDetailSerializers(serializers.ModelSerializer):
    student = StudentSerializers(read_only=True)
    faculty = FacultySerializers(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'mobile', 'username', 'user_type', 'is_admin', 'about', 'extra_fields', 'profile',
            'student', 'faculty')


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
