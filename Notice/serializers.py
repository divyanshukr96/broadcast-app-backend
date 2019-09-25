from rest_framework import serializers

from Notice.models import Notice, Image


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class NoticeSerializers(serializers.ModelSerializer):
    images = ImageSerializers(many=True, required=False)

    class Meta:
        model = Notice
        read_only_fields = ('user',)
        fields = ('title', 'description', 'date', 'time', 'venue', 'public_notice', 'department', 'images')

    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        try:
            img = validated_data.pop('images')
        except:
            pass
        departments = validated_data.pop('department')
        notice = Notice.objects.create(**validated_data)
        if departments:
            notice.department.set(departments)
        for image_data in images_data.values():
            Image.objects.create(notice=notice, image=image_data)
        return notice

    # def update(self, instance, validated_data):
    #     pass


class PublicNoticeSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('is_named_bar')
    images = serializers.SerializerMethodField('notice_images')
    created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M%p")

    class Meta:
        model = Notice
        fields = ('id', 'title', 'description', 'date', 'time', 'venue', 'user', 'images', 'created_at')

    @staticmethod
    def is_named_bar(foo):
        return foo.user.name

    def notice_images(self, foo):
        request = self.context.get('request')
        data = foo.image_set.all()
        if data:
            return list(map(lambda d: request.build_absolute_uri(d.image.url), data))
        return
