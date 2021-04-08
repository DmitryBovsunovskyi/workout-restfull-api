from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('email-verify/', views.VerifyEmailView.as_view(), name='email-verify'),
    path('password-reset/', views.PasswordResetEmail.as_view(), name='password-reset-email'),
    path('password-reset-confirm/<token>/', views.PasswordResetView.as_view(), name='password-reset-confirm'),

]
