import re
from rest_framework import serializers


def validate_phone_number(value):
    regex='09(\d{9})$'
    if re.search(regex, value):
        return value
    else:
        raise serializers.ValidationError("invalid phone number")

class PhoneTokenSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[validate_phone_number], required=True)



