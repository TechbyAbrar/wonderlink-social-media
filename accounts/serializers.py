#accounts/serializers.py
from rest_framework import serializers
from .models import UserAuth
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from locations.models import Country

from .utils import (send_mail, send_otp_email, generate_otp,
                    get_otp_expiry, generate_tokens_for_user,
                    validate_facebook_token, validate_google_token)

from nanoid import generate

class UserSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d'])
    # Override country and lives_in fields to accept codes
    country = serializers.SlugRelatedField(
        slug_field="country_code",
        queryset=Country.objects.all(),
        required=False
    )
    lives_in = serializers.SlugRelatedField(
        slug_field="country_code",
        queryset=Country.objects.all(),
        required=False
    )
    
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    # travel_lists = serializers.SerializerMethodField()
    
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAuth
        fields = [
            'id', 'email', 'full_name', 'username', 'profile_pic',
            'phone', 'dob', 'country', 'lives_in', 'public_profile', 'connect_contacts', 'is_verified', 'is_superuser', 'is_staff', 'followers_count', 'following_count',
            'date_joined', 'updated_at', 'travel_lists'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'is_superuser', 'is_staff','date_joined', 'updated_at']
        
    def get_profile_pic(self, obj):
        if obj.profile_pic_url:  # Google or remote URL
            return obj.profile_pic_url
        if obj.profile_pic:  # local uploaded file
            return obj.profile_pic.url
        return '/media/default_profile_pic.png'  # fallback
        
        



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserAuth
        fields = ['email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'password': 'Password and confirm password do not match.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        # Step 1: Take email prefix
        email_prefix = validated_data['email'].split('@')[0]

        # Step 2: Truncate to 12 characters
        base_username = email_prefix[:12]

        # Step 3: Ensure uniqueness
        username = base_username
        while UserAuth.objects.filter(username=username).exists():
            # Append a short unique suffix if collision
            suffix = generate(size=4)  # small, unique random string
            username = f"{base_username}_{suffix}"

        user = UserAuth(
            email=validated_data['email'],
            username=username,
            is_verified=True
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            user = UserAuth.objects.get(email=email)
        except UserAuth.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.is_verified:
            raise serializers.ValidationError("Email is already verified.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        if user.otp_expired and timezone.now() > user.otp_expired:
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        attrs['user'] = user
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = UserAuth.objects.get(email=value)
        except UserAuth.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")

        if user.is_verified:
            raise serializers.ValidationError("This email is already verified.")

        self.user = user  # Temporarily store the user
        return value

    def validate(self, attrs):
        attrs['user'] = self.user  # Add user to validated_data
        return attrs
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Pass email as username because default backend settings expects 'username'
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is disabled.")

        if not user.is_verified:
            raise serializers.ValidationError("Email is not verified. Please verify your email first.")

        attrs['user'] = user
        return attrs
    


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = UserAuth.objects.get(email=email)
        except UserAuth.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")
        
        if not user.is_verified:
            raise serializers.ValidationError("Email is not verified. Please verify your email first.")
        
        attrs['user'] = user
        return attrs
    
class VerifyForgetPasswordOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4, required=True)

    def validate(self, attrs):
        otp = attrs.get('otp')

        try:
            user = UserAuth.objects.get(otp=otp)
        except UserAuth.DoesNotExist:
            raise serializers.ValidationError({'email': 'User not found.'})

        if user.otp != otp:
            raise serializers.ValidationError({'otp': 'Invalid OTP.'})
        
        if user.otp_expired and timezone.now() > user.otp_expired:
            raise serializers.ValidationError({'otp': 'OTP has expired.'})

        attrs['user'] = user
        return attrs

            

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if not new_password or not confirm_password:
            raise serializers.ValidationError("New Password and Confirm Password cannot be empty.")

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        user = self.context.get('user')
        if user is None:
            raise serializers.ValidationError("User context not provided.")

        attrs['user'] = user
        return attrs
        


# social auth

# class GoogleAuthSerializer(serializers.Serializer):
#     id_token = serializers.CharField()

#     def validate(self, attrs):
#         id_token = attrs.get("id_token")
#         print("ID Token:", id_token)  # Debugging line

#         google_data = validate_google_token(id_token)
#         print("Google data:", google_data)  # Debugging line

#         if not google_data or not google_data.get("email"):
#             raise serializers.ValidationError("Invalid Google token or missing email.")

#         try:
#             user, created = UserAuth.objects.get_or_create(
#                 email=google_data["email"],
#                 defaults={
#                     "full_name": google_data.get("name", ""),
#                 },
#             )
#         except Exception:
#             raise serializers.ValidationError("Could not create or retrieve user.")

#         if created:
#             user.set_unusable_password()
#             user.is_verified = True
#             user.save()

#         tokens = generate_tokens_for_user(user)

#         return {
#             'success': True,
#             'message': 'User authenticated successfully',
#             "access": tokens['access'],
#             "refresh": tokens['refresh'],
#             'data': {"user_profile": UserSerializer(user).data}
#         }

from django.utils.crypto import get_random_string



from django.utils.crypto import get_random_string
class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(required=False)
    google_id = serializers.CharField(required=False)
    picture = serializers.URLField(required=False)  # matches incoming JSON

    def validate(self, attrs):
        if attrs.get("id_token"):
            # Validate token from Google
            google_data = validate_google_token(attrs["id_token"])
            if not google_data or not google_data.get("email"):
                raise serializers.ValidationError("Invalid or expired Google token.")
        else:
            if not attrs.get("email"):
                raise serializers.ValidationError("Email is required if no id_token provided.")
            google_data = {
                "email": attrs.get("email"),
                "name": attrs.get("full_name", ""),
                "sub": attrs.get("google_id"),
                "profile_pic": attrs.get("picture", ""),  # use correct key
            }

        attrs["google_data"] = google_data
        return attrs

    def create(self, validated_data):
        google_data = validated_data["google_data"]

        # Generate unique username
        email_prefix = google_data["email"].split("@")[0][:8]
        username = f"{email_prefix}{get_random_string(4)}"
        while UserAuth.objects.filter(username=username).exists():
            username = f"{email_prefix}{get_random_string(4)}"

        # Get or create user
        user, created = UserAuth.objects.get_or_create(
            email=google_data["email"],
            defaults={
                "full_name": google_data.get("name", ""),
                "username": username
            }
        )

        if created:
            user.set_unusable_password()
            user.is_verified = True

        # Always update Google profile picture
        if google_data.get("profile_pic") and user.profile_pic_url != google_data["profile_pic"]:
            user.profile_pic_url = google_data["profile_pic"]

        # Optional: only update full_name if it’s empty
        if not user.full_name and google_data.get("name"):
            user.full_name = google_data["name"]

        user.save()

        # Generate JWT tokens
        tokens = generate_tokens_for_user(user)

        return {
            "success": True,
            "message": "User authenticated successfully",
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "data": {
                "user_profile": UserSerializer(user).data  # profile_pic will return correct URL
            },
        }


        

class FacebookAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def validate(self, attrs):
        access_token = attrs.get("access_token")

        facebook_data = validate_facebook_token(access_token)

        if not facebook_data or not facebook_data.get("email"):
            raise serializers.ValidationError("Invalid Facebook token or missing email.")

        try:
            user, created = UserAuth.objects.get_or_create(
                email=facebook_data["email"],
                defaults={
                    "full_name": facebook_data.get("name", ""),
                },
            )
        except Exception:
            raise serializers.ValidationError("Could not create or retrieve user.")

        if created:
            user.set_unusable_password()
            user.is_verified = True
            user.save()

        tokens = generate_tokens_for_user(user)

        return {
            'success': True,
            'message': 'User authenticated successfully',
            "access": tokens['access'],
            "refresh": tokens['refresh'],
            'data': {"user_profile": UserSerializer(user).data}
        }



import jwt


class AppleAuthSerializer(serializers.Serializer):
    identity_token = serializers.CharField()

    def validate(self, attrs):
        identity_token = attrs.get("identity_token")
        print("Apple Identity Token:", identity_token)  # Debug

        try:
            # Decode the JWT identity token sent by Apple
            apple_data = jwt.decode(identity_token, options={"verify_signature": False})
            # You can also implement full signature verification using Apple's public keys
            print("Decoded Apple data:", apple_data)
        except jwt.PyJWTError:
            raise serializers.ValidationError("Invalid Apple identity token.")

        email = apple_data.get("email")
        full_name = apple_data.get("name", "")  # optional

        if not email:
            raise serializers.ValidationError("Apple token missing email.")

        try:
            user, created = UserAuth.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": full_name,
                },
            )
        except Exception:
            raise serializers.ValidationError("Could not create or retrieve user.")

        if created:
            user.set_unusable_password()
            user.is_verified = True
            user.save()

        tokens = generate_tokens_for_user(user)

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user_profile": {"id": user.id, "email": user.email, "full_name": user.full_name}
        }


# Dashboard
class AdminUserMinimalSerializer(serializers.ModelSerializer):
    living = serializers.CharField(source='lives_in.country_code', default=None)
    visited = serializers.IntegerField(read_only=True)  # number of visited countries

    class Meta:
        model = UserAuth
        fields = [
            'id',           # SI No.
            'profile_pic',  # Image
            'full_name',    # Name
            'dob',          # Born
            'phone',        # Phone
            'email',        # Email
            'living',       # Living
            'visited',      # Visited countries count
            'date_joined',  # Date
        ]