from rest_framework import serializers

from Notice.models import Notice, Department


class NoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
        read_only_fields = ('viewed',)
        fields = "__all__"


class DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

