from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework.response import Response
from rest_framework import generics, views, status, permissions, authentication
from rest_framework.authtoken.models import Token
import jwt

from user import serializers
from user.utils import (send_email_verify,
                        send_email_password_reset,
                        normalize_email,
                        decode_token_to_get_user
                        )


class RegisterUserView(generics.GenericAPIView):
    """
    Register a new user in the system
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.UserSerializer

    def post(self, request, format=None):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = get_object_or_404(get_user_model(), email=user_data['email'])
        send_email_verify(user, request)

        return Response({
               'user': user_data,
               'message': 'Link for email verification was sent to provided email address'},
                status=status.HTTP_201_CREATED
        )


class VerifyEmailView(views.APIView):
    """
    Verify a user by email with sent token
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.EmailVerificationSerializer

    def get(self, request, format=None):

        try:
            token = request.GET.get('token')

            # decode token to get user id
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=['HS256']
                )
            user = get_object_or_404(get_user_model(), id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({'email': 'Successfully activated!'}, status=status.HTTP_200_OK)
        # in case token is expired
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired!'}, status=status.HTTP_400_BAD_REQUEST)
        # in case token is invalid
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    """
    Login user into the system and create token for user
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(
                username=email,
                password=password
            )

            if user:
                if user.is_verified:
                    if user.is_active:
                        token, created = Token.objects.get_or_create(user=user)
                        # if user is already logged in
                        if token.key == str(request.auth):
                            return Response({'detail': 'You are already logged in.'},
                                            status=status.HTTP_403_FORBIDDEN)
                        else:
                            return Response({'token': token.key},
                                            status=status.HTTP_200_OK)
                    else:
                        content = {'detail': 'User account not active.'}
                        return Response(content,
                                        status=status.HTTP_401_UNAUTHORIZED)
                else:
                    content = {'detail':
                               'User account is not verified.'}
                    return Response(content, status=status.HTTP_401_UNAUTHORIZED)
            else:
                content = {'detail':
                           'Unable to login with provided credentials.'}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    """
    Logout user deletting token in the database
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Remove all auth tokens owned by request.user.
        """
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        content = {'success': f"User {request.user} has logged out successfully."}
        return Response(content, status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user
    """
    serializer_class = serializers.UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated),

    def get_object(self):
        """
        Retrieve and return authenticated user
        """
        # sending email verification if user updated email
        user = get_object_or_404(get_user_model(), email=self.request.user.email)
        if user.email != self.request.data.get('email'):
            changed_email = normalize_email(self.request.data.get('email'))
            if changed_email != None:
                send_email_verify(user, self.request, changed_email)
                user.is_verified = False
                user.save()

        return user


class PasswordResetEmail(generics.GenericAPIView):
    """
    Password reset email for the user
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ResetPasswordEmailSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data.get('email')
        user = get_object_or_404(get_user_model(), email=email)

        send_email_password_reset(user, request)

        return Response(
                    {'success': 'The link to reset your password was sent to email.'},
                    status=status.HTTP_200_OK
                    )


class PasswordResetView(generics.GenericAPIView):
    """
    Checking sent token to reset password
    and setting new password for user
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.SetNewPasswordSerializer

    def get(self, request, token, format=None):
        """
        Check if reset link is valid
        """
        # if sent token expired and user doesnt exist raise 404
        response = decode_token_to_get_user(token, request)

        return response

    def post(self, request, token):
        """
        Get user from decoded token and set new password
        """
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        password = serializer.data['password']

        response = decode_token_to_get_user(token, request, password)

        return response
