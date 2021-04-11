from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from rest_framework_simplejwt.tokens import RefreshToken


USER = get_user_model()


class TestBase:
    """
    Base class for base test cases divided by views
    """

    # in case programmer forgots to define will get appropriate exception
    @property
    def email(self):
        raise NotImplementedError()

    @property
    def password(self):
        raise NotImplementedError()

    @property
    def username(self):
        raise NotImplementedError()

    @property
    def payload(self):
        return {
            'email': self.email,
            'password': self.password,
            'username': self.username,
        }

    # creates user and authenticate if True
    def create_user(self, authenticated=False):
        user = USER.objects.create(
                    email=self.email,
                    password=self.password,
                    username=self.username,
        )

        user.is_verified = True
        user.save()
        if authenticated:
            token, created = Token.objects.get_or_create(user=user)
            token_key = token.key
            self.client.force_authenticate(user=user, token=token_key)

    # creates user and generate token verification for email links
    @property
    def token_verification(self):
        user = USER.objects.create(
                    email=self.email,
                    password=self.password,
                    username=self.username,
        )
        token = RefreshToken.for_user(user).access_token
        return str(token)



    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {}


    @patch('user.utils.send_email')
    def setUp(self, send_email_mocked):
        self.client = APIClient()
        self.response = self.client.post(reverse('user:register'), self.payload)
        self.send_email = send_email_mocked

    def test_should_return_expected_status_code(self):
        self.assertEqual(self.response.status_code, self.expected_status_code)


    def test_should_return_expected_payload(self):
        self.assertEqual(self.response.data, self.expected_return_payload)



class TestBaseWithEmail(TestBase):

    # for mocking email send
    expected_mock_function_call_count = 0
    expected_return_mock_called_args = {}


    def test_should_return_expected_mock_function_call_count(self):
        self.assertEqual(self.send_email.call_count, self.expected_mock_function_call_count)

    def test_should_return_expected_return_mock_called_args(self):
        if self.expected_return_mock_called_args == {}:
            self.send_email.assert_not_called()
        else:
            self.send_email.assert_called_with(self.expected_return_mock_called_args)


class TestBaseEmailVerify(TestBase):
    """
    Base test for email verification
    """

    token_valid = False

    def setUp(self):
        self.client = APIClient()
        if self.token_valid:
            self.response = self.client.get(reverse('user:email-verify') + '?token=' + self.token_verification)
        else:
            self.response = self.client.get(reverse('user:email-verify') + '?token=INVALID_TOKEN')


class TestBaseLogin(TestBase):
    """
    Base class for login user test
    """
    @property
    def payload_login(self):
        return {
            'email': self.email,
            'password': self.password,
        }
    verified = False
    registered = True
    logged_in = False

    def setUp(self):
        if self.registered:
            self.client = APIClient()
            self.response_register = self.client.post(reverse('user:register'), self.payload)
            if self.verified:
                user = USER.objects.get(email=self.email)
                user.is_verified = True
                user.save()
                self.response = self.client.post(reverse('user:login'), self.payload_login)
                # fetching user token for asserting payload and forcing auth
                token = Token.objects.get(user=user)
                self.token_key = token.key
                # testing logged_in user
                if self.logged_in:
                    self.client.force_authenticate(user=user, token=self.token_key)
                    self.response = self.client.post(reverse('user:login'), self.payload_login)
            else:
                self.response = self.client.post(reverse('user:login'), self.payload_login)
        else:
            self.client = APIClient()
            self.response = self.client.post(reverse('user:login'), self.payload)


class TestBaseLogout(TestBase):
    """
    Base class for logout user test
    """

    logged_in = False

    def setUp(self):
        self.client = APIClient()
        if self.logged_in:
            self.create_user(authenticated=True)

        self.response = self.client.get(reverse('user:logout'))


class TestBaseUserChange(TestBaseWithEmail):
    """
    Base test for updating user profile
    """
    @property
    def email_changed(self):
        raise NotImplementedError()

    @property
    def password_changed(self):
        raise NotImplementedError()

    @property
    def username_changed(self):
        raise NotImplementedError()

    @property
    def payload_update(self):
        return {
            'email': self.email_changed,
            'password': self.password_changed,
            'username': self.username_changed,
        }

    logged_in = False

    @patch('user.utils.send_email')
    def setUp(self, send_email_mocked):
        self.client = APIClient()
        self.send_email = send_email_mocked
        if self.logged_in:
            self.create_user(authenticated=True)

        self.response = self.client.patch(reverse('user:me'), self.payload_update)


class TestBaseUserResetPasswordEmail(TestBaseWithEmail):
    """
    Base test for requesting reset password link by user
    """

    email_wrong = False

    @patch('user.utils.send_email')
    def setUp(self, send_email_mocked):
        self.client = APIClient()
        self.send_email = send_email_mocked
        self.create_user()
        if self.email_wrong:
            self.response = self.client.post(reverse('user:password-reset-email'), {'email': 'wrong@mail.com'})
        else:
            self.response = self.client.post(reverse('user:password-reset-email'), {'email': self.payload['email']})

class TestBaseUserResetPasswordVerification(TestBase):
    """
    Base test for resetting password with token sent in reset link
    """
    token_valid = False

    def setUp(self):
        self.client = APIClient()
        if self.token_valid:
            self.response = self.client.get(reverse('user:password-reset-confirm', args=[self.token_verification]))
        elif not self.token_valid:
            self.response = self.client.get(reverse('user:password-reset-confirm', args=['INVALID_TOKEN']))


class TestBaseUserResetPasswordConfirm(TestBase):
    """
    Base test for resetting password with token sent in reset link
    """
    token_valid = True

    password_reset = {}

    def setUp(self):
        self.client = APIClient()
        if self.token_valid:
            self.response = self.client.post(reverse('user:password-reset-confirm', args=[self.token_verification]), self.password_reset)
        else:
            self.response = self.client.post(reverse('user:password-reset-confirm', args=['INVALID_TOKEN']), self.password_reset)
