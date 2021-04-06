from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework.response import Response
from rest_framework import generics, views, status, permissions
from rest_framework.authtoken.models import Token
import jwt

from user import serializers
from user.utils import send_email_verify


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
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=['HS256']
                )
            user = get_user_model().objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({'email': 'Successfully activated!'}, status=status.HTTP_200_OK)
        # in case token is expired
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired !'}, status=status.HTTP_400_BAD_REQUEST)
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
