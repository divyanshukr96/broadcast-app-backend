from rest_framework import serializers
from Users.models import User, Faculty, Student


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('user_type',)


class DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FacultySerializers(serializers.ModelSerializer):
    user = UserSerializers()
    user_type = serializers.ChoiceField(choices=['Faculty'])

    class Meta:
        model = Faculty
        fields = ('user', 'user_type', 'department', 'designation', 'sex', 'dob', )


class StudentSerializers(serializers.ModelSerializer):
    user = UserSerializers()

    class Meta:
        model = Student
        fields = '__all__'
