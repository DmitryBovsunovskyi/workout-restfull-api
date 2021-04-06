from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('email-verify/', views.VerifyEmailView.as_view(), name='email-verify'),
]
