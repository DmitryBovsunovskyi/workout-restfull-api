from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.utils import normalize_email


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

    def update(self, instance, validated_data):
        """
        Update a user with encrypted password and return it
        """
        password = validated_data.pop('password', None)
        email = normalize_email(validated_data.pop('email', None))
        validated_data['email'] = email
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


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


class ResetPasswordEmailSerializer(serializers.Serializer):
    """
    Serializer for sending token for rest password for user
    """
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting user password
    """
    password = serializers.CharField(max_length=128)
    password_confirmation = serializers.CharField(max_length=128)

    def validate(self, attrs):

        password = attrs.get('password', '')
        password_confirmation = attrs.get('password_confirmation', '')
        if password != password_confirmation:
            raise ValidationError(
                "Password and confirm_password does not match!"
            )
        return super().validate(attrs)
