from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
import jwt


def send_email(data):

    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=[data['to_email']]
    )
    email.send()

def send_email_verify(user, request, changed_email=None):
    """
    Sending email with link to verify user
    """
    user = get_object_or_404(get_user_model(), email=user.email)

    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relative_link = reverse('user:email-verify')

    abs_url = 'http://' + current_site + relative_link + "?token=" + str(token)

    email_body = "Hello " + user.username + '!' + ' Use link below to verify your email \n' + abs_url

    data = {
        'email_body': email_body,
        'to_email': user.email,
        'email_subject': 'Verify your email'
    }

    if changed_email:
        data['to_email'] = changed_email

    send_email(data)

def send_email_password_reset(user, request):
    """
    Send email with link to reset password for user
    """
    user = get_object_or_404(get_user_model(), email=user.email)
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relative_link = reverse(
                        'user:password-reset-confirm',
                        kwargs={'token': token}
                        )
    abs_url = 'http://' + current_site + relative_link

    email_body = "Hello,  \n Use the link below to reset your password \n" + abs_url

    data = {
        'email_body': email_body,
        'to_email': user.email,
        'email_subject': 'Reset your password'
    }

    send_email(data)


def normalize_email(email):
    """
    Normalize the address by lowercasing the domain part of the email
    address.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        # return None to leave error handling for serializer
        return None
    else:
        email = '@'.join([email_name, domain_part.lower()])
    return email

def decode_token_to_get_user(token, request, new_password=None):
    """
    Decode token to get user and set new password
    """
    try:
        # decode token to get user id
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=['HS256']
            )
        user = get_object_or_404(get_user_model(), id=payload['user_id'])

        # setting new password for user
        if request.method == 'POST' and new_password:
            user.set_password(new_password)
            user.save()
            return Response({'success': 'Password reset successfully!'}, status=status.HTTP_200_OK)

        return Response({'success': 'Reset your password'}, status=status.HTTP_200_OK)
    # in case token is invalid
    except jwt.exceptions.DecodeError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    # in case token is expired
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Reset link has expired! Request another one.'}, status=status.HTTP_400_BAD_REQUEST)
