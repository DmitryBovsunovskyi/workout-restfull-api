from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


from user.tests.utils import (
                        TestBase,
                        TestBaseWithEmail,
                        TestBaseLogin,
                        TestBaseLogout,
                        TestBaseUserChange,
                        TestBaseUserResetPasswordEmail,
                        TestBaseEmailVerify,
                        TestBaseUserResetPasswordVerification,
                        TestBaseUserResetPasswordConfirm,
                      )


USER = get_user_model()


class TestSuccessfulRegister(TestBaseWithEmail, TestCase):
    """
    Test register user with valid payload should succeed,
    email for verification should be sent
    """
    email = 'nozhuk1994@gmail.com'
    password = 'testpassword'
    username = 'testname'

    expected_status_code = status.HTTP_201_CREATED
    expected_return_payload = {
            'user': {
                'email': email,
                'username': username,
            },
            'message': 'Link for email verification was sent to provided email address'
    }
    expected_mock_function_call_count = 1

    # fetching email body from mocked function
    @property
    def called_args(self):
        expected_return_mock_called_args = {
            'email_body': self.send_email.call_args[0][0]['email_body'],
            'to_email': self.email,
            'email_subject': 'Verify your email'
        }
        return expected_return_mock_called_args

    expected_return_mock_called_args = called_args


class TestRegisterFails(TestBaseWithEmail, TestCase):
    """
    Test registering user with invlaid email, pasword and blank name fails,
    verification email is not sent
    """
    email = 'invalidemail'
    password = 'inv'
    username = ''

    expected_status_code = status.HTTP_400_BAD_REQUEST
    expected_return_payload = {
            'email': [
                "Enter a valid email address."
            ],
            "password": [
                "Ensure this field has at least 5 characters."
            ],
            "username": [
                "This field may not be blank."
            ],
    }
    expected_mock_function_call_count = 0


class TestEmailVerificationSuccessfull(TestBaseEmailVerify, TestCase):
    """
    Test verification email for user with valid token succeed
    """
    email = 'nozhuk1994@gmail.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = True

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {'email': 'Successfully activated!'}


class TestEmailVerificationFails(TestBaseEmailVerify, TestCase):
    """
    Test verification email for user with invalid token fails
    """
    email = 'nozhuk1994@gmail.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = False

    expected_status_code = status.HTTP_400_BAD_REQUEST
    expected_return_payload = {'error': 'Invalid token'}


class TestLoginSuccessfull(TestBaseLogin, TestCase):
    """
    Test login user after email verification succeed
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    # default is False
    verified = True

    expected_status_code = status.HTTP_200_OK
    #frtching user token from setUp
    @property
    def token_return(self):
        expected_payload = {'token': self.token_key}
        return expected_payload

    expected_return_payload = token_return


class TestLoginFails(TestBaseLogin, TestCase):
    """
    Test login user when email is not verified fails
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    expected_status_code = status.HTTP_401_UNAUTHORIZED

    expected_return_payload = {
            'detail': "User account is not verified."
    }


class TestLoginUnregisteredUserFails(TestBaseLogin, TestCase):
    """
    Test login unregistered user
    """

    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    # default is True
    registered = False

    expected_status_code = status.HTTP_401_UNAUTHORIZED

    expected_return_payload = {
            'detail': "Unable to login with provided credentials."
    }


class TestLoginForLoggedinUserFails(TestBaseLogin, TestCase):
    """
    Test logged in user fails to login if not logged out
    """

    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    registered = True
    verified = True
    # default is Flase
    logged_in = True

    expected_status_code = status.HTTP_403_FORBIDDEN

    expected_return_payload = {'detail': 'You are already logged in.'}


class TestLogoutSuccessfull(TestBaseLogout, TestCase):
    """
    Test logout user if user is authorized should succeed
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'
    # default False
    logged_in = True

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {'success': f"User {email} has logged out successfully."}

class TestLogoutFails(TestBaseLogout, TestCase):
    """
    Test logout for unauthorised user should fail
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    logged_in = False

    expected_status_code = status.HTTP_401_UNAUTHORIZED
    expected_return_payload = {"detail": "Authentication credentials were not provided."}


class TestSuccessfulUpdateUser(TestBaseUserChange, TestCase):
    """
    Test update user profile with valid payload should succeed,
    if email is changed, email verification should be sent
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    logged_in = True

    email_changed = 'changed@email.com'
    password_changed = 'changedpassword'
    username_changed = 'changedtestname'

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {
            "email": email_changed,
            "username": username_changed,

    }
    expected_mock_function_call_count = 1

    # fetching email body from mocked function
    @property
    def called_args(self):
        expected_return_mock_called_args = {
            'email_body': self.send_email.call_args[0][0]['email_body'],
            'to_email': self.email_changed,
            'email_subject': 'Verify your email'
        }
        return expected_return_mock_called_args

    expected_return_mock_called_args = called_args


class TestUpdateUserProfileDoesntSendEmail(TestBaseUserChange, TestCase):
    """
    Test updating user profile with unchanged email
    should not send email verification
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    logged_in = True

    # email is not changed
    email_changed = 'test@email.com'
    password_changed = 'changedpassword'
    username_changed = 'changedtestname'

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {
            "email": email_changed,
            "username": username_changed,

    }
    expected_mock_function_call_count = 0


class TestUpdateUserProfileFails(TestBaseUserChange, TestCase):
    """
    Test updating unauthenticated user fails,
    email verification should not be sent
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    logged_in = False

    email_changed = 'test@email.com'
    password_changed = 'changedpassword'
    username_changed = 'changedtestname'

    expected_status_code = status.HTTP_401_UNAUTHORIZED
    expected_return_payload = {
            "detail": "Authentication credentials were not provided."
    }
    expected_mock_function_call_count = 0


class TestPasswordResetEmailSuccessfull(TestBaseUserResetPasswordEmail, TestCase):
    """
    Test  should send email reset link to user with provided email that exists
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {
            'success': 'The link to reset your password was sent to email.'
    }

    expected_mock_function_call_count = 1

    # fetching email body from mocked function
    @property
    def called_args(self):
        expected_return_mock_called_args = {
            'email_body': self.send_email.call_args[0][0]['email_body'],
            'to_email': self.email,
            'email_subject': 'Reset your password'
        }
        return expected_return_mock_called_args

    expected_return_mock_called_args = called_args


class TestPasswordResetEmailFails(TestBaseUserResetPasswordEmail, TestCase):
    """
    Test shouldn`t send email reset link to user with provided email that doesn`t exist
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    email_wrong = True

    expected_status_code = status.HTTP_404_NOT_FOUND
    expected_return_payload = {
            'detail': 'Not found.'
    }

    expected_mock_function_call_count = 0


class TestPasswordResetTokenVerifySuccessfull(TestBaseUserResetPasswordVerification, TestCase):
    """
    Test verifying token sent for resetting password succeed with valid token
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = True

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {'success': 'Reset your password'}


class TestPasswordResetTokenVerifyFails(TestBaseUserResetPasswordVerification, TestCase):
    """
    Test verifying token sent for resetting password fails with invalid token
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = False

    expected_status_code = status.HTTP_400_BAD_REQUEST
    expected_return_payload = {'error': 'Invalid token'}


class TestPasswordResetConfirmSuccessfull(TestBaseUserResetPasswordConfirm, TestCase):
    """
    Test resetting password for user with valid token and
    correct confirm password should succeed
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = True

    password_reset = {
            'password': 'newpassword',
            'password_confirmation': 'newpassword',
    }

    expected_status_code = status.HTTP_200_OK
    expected_return_payload = {'success': 'Password reset successfully!'}


class TestPasswordResetConfirmFails(TestBaseUserResetPasswordConfirm, TestCase):
    """
    Test resetting password for user with invalid token and
    correct confirm password should fail
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = False

    password_reset = {
            'password': 'newpassword',
            'password_confirmation': 'newpassword',
    }

    expected_status_code = status.HTTP_400_BAD_REQUEST
    expected_return_payload = {'error': 'Invalid token'}


class TestPasswordResetConfirmMismatch(TestBaseUserResetPasswordConfirm, TestCase):
    """
    Test resetting password for user with valid token but
    mismatched confirm password should fail
    """
    email = 'test@email.com'
    password = 'testpassword'
    username = 'testname'

    token_valid = True

    password_reset = {
            'password': 'newpassword',
            'password_confirmation': 'newpassworddddd',
    }

    expected_status_code = status.HTTP_400_BAD_REQUEST
    expected_return_payload = {
            "non_field_errors": ["Password and confirm_password does not match!"]
    }
