from django.utils.timezone import now
from rest_framework import serializers

from Notice.models import Notice, Image


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class NoticeSerializers(serializers.ModelSerializer):
    images = ImageSerializers(many=True, required=False)
    images_list = serializers.SerializerMethodField('notice_images')

    class Meta:
        model = Notice
        read_only_fields = ('user',)
        fields = (
            'id', 'title', 'description', 'date', 'time', 'venue', 'public_notice', 'department', 'images_list',
            'images', 'is_event')

    def notice_images(self, notice):
        request = self.context.get('request')
        data = notice.image_set.all()
        if data:
            return list(map(lambda d: {
                'id': d.id,
                'url': request.build_absolute_uri(d.image.url)
            }, data))
        return

    def create(self, validated_data):
        departments = ""
        images_data = self.context.get('view').request.FILES
        try:
            img = validated_data.pop('images')
        except KeyError:
            pass
        try:
            departments = validated_data.pop('department')
        except KeyError:
            pass
        notice = Notice.objects.create(**validated_data)
        if departments:
            notice.department.set(departments)
        for image_data in images_data.values():
            Image.objects.create(notice=notice, image=image_data)
        return notice

    def update(self, instance, validated_data):
        images_data = self.context.get('view').request.FILES

        if len(images_data) > 0:
            temp_img = Image.objects.filter(notice=instance)
            # for img in temp_img:
            #     img.delete()
            for image_data in images_data.values():
                Image.objects.create(notice=instance, image=image_data)

        try:
            img = validated_data.pop('images')
        except KeyError:
            pass

        try:
            departments = validated_data.pop('department')
            if departments:
                instance.department.set(departments)
        except KeyError:
            pass

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)

        instance.is_event = validated_data.get('is_event', instance.is_event)
        instance.venue = validated_data.get('venue', instance.venue)
        instance.date = validated_data.get('date', instance.date)
        instance.time = validated_data.get('time', instance.time)

        instance.public_notice = validated_data.get('public_notice', instance.public_notice)

        instance.save()

        return instance


class PublicNoticeSerializers(serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField('is_named_bar')
    images = serializers.SerializerMethodField('notice_images')
    images_list = serializers.SerializerMethodField('notice_images_list')
    profile = serializers.SerializerMethodField('user_profile')
    created_at = serializers.DateTimeField(format="%d-%m-%Y, %H:%M")
    time = serializers.TimeField(format="%H:%M")

    class Meta:
        model = Notice
        fields = (
            'id', 'title', 'description', 'is_event', 'date', 'time', 'venue', 'user', 'profile', 'images',
            'images_list', 'department', 'public_notice', 'can_edit', 'created_at')

    def get_can_edit(self, notice):
        request = self.context.get('request')
        if notice.user.user_type in ['DEPARTMENT', 'SOCIETY'] and notice.user == request.user:
            return (now() - notice.created_at).days <= 1
        return False

    @staticmethod
    def is_named_bar(notice):
        return notice.user.name

    def user_profile(self, notice):
        request = self.context.get('request')
        if notice.user.profile:
            return request.build_absolute_uri(notice.user.profile.url)

    def notice_images(self, notice):
        request = self.context.get('request')
        data = notice.image_set.all()
        if data:
            return list(map(lambda d: request.build_absolute_uri(d.image.url), data))
        return

    def notice_images_list(self, notice):
        request = self.context.get('request')
        data = notice.image_set.all()
        if data:
            return list(map(lambda d: {
                'id': d.id,
                'url': request.build_absolute_uri(d.image.url)
            }, data))
        return


class NoticeImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
