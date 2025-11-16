#accounts/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import (
    SignupSerializer, VerifyEmailOTPSerializer,
    UserSerializer, ResendOTPSerializer, LoginSerializer,
    ForgetPasswordSerializer, ResetPasswordSerializer, FacebookAuthSerializer, GoogleAuthSerializer, ContactMatchUserSerializer
)
from .utils import generate_otp, send_otp_email, generate_tokens_for_user
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from .permissions import  IsOwnerOrSuperuser, IsSuperUserOrReadOnly
from rest_framework.permissions import IsAuthenticated
from .models import UserAuth

import logging
logger = logging.getLogger(__name__)

from django.db import transaction
# Create your views here.
from rest_framework.parsers import MultiPartParser, FormParser

class SignupView(APIView):
    permission_classes = [AllowAny]
    # parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                tokens = generate_tokens_for_user(user)

                logger.info(f"Signup successful for {user.email}")

                return Response({
                    'success': True,
                    'message': 'Signup successful.',
                    'access_token': tokens['access'],
                    'profile_pic_url': request.build_absolute_uri(user.profile_pic.url) if user.profile_pic else None
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Signup error: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'An error occurred during signup.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Signup validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Validation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmailOTPView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = VerifyEmailOTPSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                user.is_verified = True
                user.otp = None
                user.otp_expired = None
                user.save()

                tokens = generate_tokens_for_user(user)

                logger.info(f"Email verified for user: {user.email}")
                return Response({
                    'success': True,
                    'message': 'Email verified successfully.',
                    'access_token': tokens['access'],
                    # 'refresh_token': tokens['refresh']
                }, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Email verification error: {str(e)}", exc_info=True)
                return Response({
                    'error': 'Email verification failed. Please try again later.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Email verification failed: {serializer.errors}")
        return Response({
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    # throttle_classes = [ResendOTPThrottle]

    @transaction.atomic
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                user.set_otp()
                user.save()

                send_otp_email(user.email, user.otp)
                logger.info(f"New OTP sent to {user.email}")

                return Response({
                    'success': True,
                    'message': 'A new OTP has been sent to your email.'
                }, status=status.HTTP_200_OK)

            except Exception as e:
                logger.exception("Error while resending OTP")  # cleaner log
                return Response({
                    'success': False,
                    'message': 'Failed to resend OTP. Please try again later.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Resend OTP validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Validation failed. Please check your input and try again.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     permission_classes = [AllowAny]
#     # throttle_classes = [LoginThrottle]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 user = serializer.validated_data['user']
#                 tokens = generate_tokens_for_user(user)

#                 logger.info(f"User {user.email} logged in successfully.")

#                 return Response({
#                     'success': True,
#                     'message': 'Login successful!',
#                     'access_token': tokens['access'],
#                     'refresh_token': tokens['refresh'],
#                     'data' :{
#                         'user': UserSerializer(user).data
#                     }
#                 }, status=status.HTTP_200_OK)

#             except Exception as e:
#                 logger.error(f"Unexpected error during login for {request.data.get('email')}: {str(e)}", exc_info=True)
#                 return Response({
#                     'success': False,
#                     'message': 'Login failed. Please check your credentials.',
#                     'error': str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         logger.warning(f"Login validation failed: {serializer.errors}")
#         return Response({
#             'success': False,
#             'message': 'Validation failed. Please check everything properly and try again.',
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']

                # ===== Sync Travel Records =====
                user.sync_travel_records()  # <-- ensures country and lives_in are synced

                # Generate tokens
                tokens = generate_tokens_for_user(user)

                logger.info(f"User {user.email} logged in successfully.")

                return Response({
                    'success': True,
                    'message': 'Login successful!',
                    'access_token': tokens['access'],
                    'refresh_token': tokens['refresh'],
                    'data': {
                        'user': UserSerializer(user).data  # travel_lists now synced
                    }
                }, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Unexpected error during login for {request.data.get('email')}: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'Login failed. Please check your credentials.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Login validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Validation failed. Please check everything properly and try again.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


        
        
class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]
    # throttle_classes = [ForgetPassThrottle]
    
    def post(self, request):
        serializer = ForgetPasswordSerializer(data = request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                user.set_otp()
                user.save()
                
                send_otp_email(user.email, user.otp)
                logger.info(f"OTP for password reset sent to {user.email}")
                return Response({
                    'success': True,
                    'message': 'OTP for password reset sent to your email.'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error while sending OTP for password reset: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'Failed to send OTP for password reset. Please try again later.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        logger.warning(f"Forget password validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Validation failed. Please check your input and try again.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)  
        
from .serializers import VerifyForgetPasswordOTPSerializer

class VerifyForgetPasswordOTPView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = VerifyForgetPasswordOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate access token only (no refresh)
            token = generate_tokens_for_user(user)
            access_token = token['access']

            return Response({
                'success': True,
                'message': 'OTP verified. You may now reset your password.',
                'access_token': access_token,
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': 'OTP verification failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrSuperuser]  
    # throttle_classes = [ResetPassThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data, context={'user': request.user})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']

            try:
                user.set_password(new_password)
                user.save()
                logger.info(f"Password reset successfully for user: {user.email}")
                return Response({'success':True,'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error resetting password for {user.email}: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'Failed to reset password. Please try again later.',
                    'error': 'Failed to reset password. Please try again later.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Reset password validation failed for user {request.user.email if request.user else 'Anonymous'}: {serializer.errors}")
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrSuperuser]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'message': 'User profile retrieved successfully.',
            'data':{'user': serializer.data}
            }, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"User profile updated successfully for {user.email}")
                return Response({
                    'success':True,
                    'message': 'Profile updated successfully.',
                    'data':{'user': serializer.data}
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating user profile for {user.email}: {str(e)}", exc_info=True)
                return Response({'error': 'Failed to update profile. Please try again later.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Profile update validation failed for {user.email}: {serializer.errors}")
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





            
class SpecificUserView(APIView):
    # permission_classes = [IsOwnerOrSuperuser]

    def get(self, request, pk):
        user = request.user
        # if not user.is_superuser:
        #     logger.warning(f'Unauthorized detail access by user: {user.id}')
        #     return Response({
        #         'success': False,
        #         'message': 'Permission denied. Only admin can access this.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_obj = UserAuth.objects.get(pk=pk)
            serializer = UserSerializer(user_obj)
            logger.info(f'Superuser {user.id} accessed data for user {pk}')
            return Response({
                'success': True,
                'message': 'User data retrieved successfully.',
                'data':{'user': serializer.data}
                }, status=status.HTTP_200_OK)
        except UserAuth.DoesNotExist:
            logger.error(f'User with ID {pk} not found.')
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        


# social auth

class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()  # ✅ calls create() internally
            return Response(data, status=status.HTTP_200_OK)
        return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    



class FacebookLoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = FacebookAuthSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"success": True, "data": serializer.validated_data}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


from .serializers import AppleAuthSerializer


class AppleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AppleAuthSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    "success": True,
                    "message": "User authenticated successfully",
                    "data": serializer.validated_data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Apple login failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )




# Admin user list view with pagination and optimized queries
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from accounts.models import UserAuth
from .serializers import AdminUserMinimalSerializer
from rest_framework import status
from rest_framework.response import Response

# ---------------- Standard response helpers ----------------
def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response(
        {"success": True, "message": message, "data": data},
        status=status_code
    )

def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {"success": False, "message": message, "data": None},
        status=status_code
    )

# ---------------- Pagination ----------------
class AdminUserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

# ---------------- Admin User List API ----------------
class AdminUserListAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            # ---------------- Optimized Query ----------------
            users_qs = (
                UserAuth.objects.select_related('lives_in')
                .annotate(
                    visited=Count('travel_records', filter=Q(travel_records__visited=True))
                )
                .order_by('-date_joined')
            )

            # ---------------- Pagination ----------------
            paginator = AdminUserPagination()
            page = paginator.paginate_queryset(users_qs, request)

            serializer = AdminUserMinimalSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return error_response(f"Something went wrong: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)



# contact match
class ContactMatchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contacts = request.data.get("contacts")

        if not contacts or not isinstance(contacts, list):
            return Response({"error": "contacts must be a non-empty list"}, status=400)

        normalized = [c.replace(" ", "").replace("-", "") for c in contacts]

        matched = UserAuth.objects.filter(
            phone__in=normalized,
            is_active=True,
            public_profile=True,
            connect_contacts=True,
        ).only("full_name", "username", "profile_pic", "profile_pic_url")

        data = ContactMatchUserSerializer(matched, many=True).data

        return Response({"matched_users": data})