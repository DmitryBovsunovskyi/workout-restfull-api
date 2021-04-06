from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the users object
    """
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it
        """
        return get_user_model().objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the token of user object
    """
    token = serializers.CharField(max_length=555)

class LoginSerializer(serializers.Serializer):
    """
    Serializer to login user
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)
