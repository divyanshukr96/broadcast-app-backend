from rest_framework.authtoken.models import Token
from rest_framework.compat import coreapi, coreschema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.views import APIView
from .models import PasswordToken
from .serializers import PasswordTokenSerializer, OTPConfirmSerializer, PasswordChangeSerializer


class ObtainPasswordToken(APIView):
    throttle_classes = ()
    serializer_class = PasswordTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for password reset",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['email']
        token, created = PasswordToken.objects.get_or_create(user=user)
        if token.expired():
            token.delete()
            token, created = PasswordToken.objects.get_or_create(user=user)
        return Response({'token': token.key})


obtain_password_token = ObtainPasswordToken.as_view()


class PasswordResetConfirm(APIView):
    serializer_class = OTPConfirmSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="token",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Token",
                        description="Valid token for verify user",
                    ),
                ),
                coreapi.Field(
                    name="otp",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="OTP",
                        description="Valid otp for verify the token",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request}, )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if user:
            token, created = Token.objects.get_or_create(user=user)
            if not created:
                token.delete()
                token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'otp': "Something went wrong"}, 400)


password_reset_confirm = PasswordResetConfirm.as_view()


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        auth_token = Token.objects.filter(user=request.user).first()
        if auth_token:
            auth_token.delete()

        return Response({"detail": "New password has been saved."})


password_reset_change = PasswordChangeView.as_view()
