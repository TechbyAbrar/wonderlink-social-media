from django.urls import path
from .views import (SignupView, VerifyEmailOTPView, ResendOTPView,
                    LoginView, ForgetPasswordView, ResetPasswordView, UpdateProfileView, 
                    SpecificUserView, VerifyForgetPasswordOTPView, GoogleLoginAPIView, FacebookLoginAPIView, AdminUserListAPIView, AppleLoginAPIView)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailOTPView.as_view(), name='verify-email-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget-password'),
    path('verify/pass/otp/', VerifyForgetPasswordOTPView.as_view(), name='forget-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('user/<int:pk>/', SpecificUserView.as_view(), name='specific-user'),
    path('googleLogin/', GoogleLoginAPIView.as_view(), name='google-login'),
    path('facebookLogin/', FacebookLoginAPIView.as_view(), name='facebook-login'),
    path('apple-login/', AppleLoginAPIView.as_view(), name='apple-login'),
    path('dashboard/users-list/', AdminUserListAPIView.as_view(), name='admin-user-list'),
    
]