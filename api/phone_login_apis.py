from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PhoneTokenSerializer
from ..models import PhoneToken
from drf_spectacular.utils import extend_schema


class GenerateTokenApi(APIView):

    @extend_schema(request=PhoneTokenSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PhoneTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_token = PhoneToken.objects.get_or_create(
            phone_number=serializer.validated_data.get('phone_number'),
        )[0]
        print
        token = PhoneToken.send_otp(phone_token)
        return Response(
            {'OTP code': token}
        )
