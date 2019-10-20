from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from password_reset.models import PasswordToken


class PasswordTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"), required=True, trim_whitespace=True)

    @staticmethod
    def validate_email(email):
        if email:
            try:
                user = get_user_model().objects.get(email=email)
                if user.is_active and user.username:
                    return user
                raise
            except get_user_model().DoesNotExist:
                pass
        raise serializers.ValidationError("Invalid credentials provided")

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class OTPConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(label=_("Token"), required=True)
    otp = serializers.CharField(
        label=_("OTP"),
        trim_whitespace=False,
        required=True
    )

    @staticmethod
    def validate_token(token):
        try:
            user = PasswordToken.objects.get(key=token)
            if user:
                return token
            else:
                raise
        except PasswordToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token entered')

    def validate_otp(self, otp):
        try:
            token = self.initial_data.get('token')
            user = PasswordToken.objects.get(key=token)
            if user.expired():
                pass
            elif user.otp == otp:
                return user
            else:
                raise
        except PasswordToken.DoesNotExist:
            raise serializers.ValidationError('Something went wrong')
        except:
            raise serializers.ValidationError('Invalid OTP entered')

        raise serializers.ValidationError('OTP entered is expired.')

    def validate(self, attrs):
        token = attrs.get('otp')
        if token and token.user:
            return token.user
        else:
            raise serializers.ValidationError({
                'token': "Invalid token entered"
            }, 404)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, required=True)
    token = serializers.CharField(max_length=128, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_token(self, token):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        try:
            if user and user.password_reset_token.first().key == token:
                return token
        except:
            pass
        raise serializers.ValidationError('Incorrect details')

    def save(self, **kwargs):
        request = self.context.get('request')
        password = self.data.get('password')
        user = getattr(request, 'user', None)
        if user and password:
            user.set_password(password)
            user.save()
            try:

                user.password_reset_token.first().delete()
            except:
                pass
