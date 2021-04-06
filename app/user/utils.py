from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken


def send_email(data):

    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=[data['to_email']]
    )
    email.send()

def send_email_verify(user, request):
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

    send_email(data)
