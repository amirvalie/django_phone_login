from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import PhoneToken
from drf_spectacular.utils import extend_schema
from django.contrib.auth import (
    authenticate, login
)
from .serializers import PhoneTokenSerializer, ConfirmTokenSerializer
from .permissions import IsNotAuthenticated
from ..limit_request import GenerateLimitation

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
        GenerateLimitation(request)
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
            'otp is not valid',
            status=status.HTTP_400_BAD_REQUEST
        )
