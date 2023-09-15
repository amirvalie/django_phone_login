from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import PhoneToken
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate, login
from .serializers import PasswordLoginSerializer, PhoneTokenSerializer, ConfirmTokenSerializer
from .permissions import IsNotAuthenticated
from ..limit_request import GenerateLimitation
from django.contrib.auth import get_user_model

User = get_user_model()

class GenerateTokenApi(APIView):
    permission_classes = [IsNotAuthenticated]

    @extend_schema(request=PhoneTokenSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PhoneTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_token = PhoneToken.objects.get_or_create(
            phone_number=serializer.validated_data.get('phone_number'),
        )[0]
        PhoneToken.send_otp(phone_token)
        return Response(
            {'otp': phone_token.otp},
            status=status.HTTP_200_OK
        )


class ConfirmTokenApi(APIView):

    @extend_schema(request=ConfirmTokenSerializer)
    def post(self, request):
        serializer = ConfirmTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data.get('otp'))
        user = authenticate(
            self.request,
            otp=serializer.validated_data.get('otp'),
            phone_number=serializer.validated_data.get('phone_number'),
        )
        if user is not None:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return Response(
                'User authenticated successfully',
                status=status.HTTP_200_OK
            )
        return Response(
            'otp is not valid!',
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordLoginApi(APIView):
    @extend_schema(request=PasswordLoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data.get('phone_number'),
            password=serializer.validated_data.get('password'),
        )
        if user:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return Response(
                'User authenticated successfully',
                status=status.HTTP_200_OK
            )
        return Response(
                'username or password is not valid! \n or may be you did not specify a password',
                status=status.HTTP_400_BAD_REQUEST
            )
