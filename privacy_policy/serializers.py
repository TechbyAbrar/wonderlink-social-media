from rest_framework import serializers
from .models import (PrivacyPolicy, TrustSafety, TermsConditions, GetInTouch as ContactForm, AboutUs, OurStory, DataManagement, AcccountManagement, paymentQuries)

class BaseContentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'description', 'last_updated']
        read_only_fields = ['id', 'last_updated']

class PrivacyPolicySerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = PrivacyPolicy

class TrustSafetySerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = TrustSafety

class TermsConditionsSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = TermsConditions
        
        
class AboutUsSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = AboutUs
        
class OurStorySerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = OurStory
        
class DataManagementSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = DataManagement
        
class AcccountManagementSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = AcccountManagement
        
class PaymentQueriesSerializer(BaseContentSerializer):
    class Meta(BaseContentSerializer.Meta):
        model = paymentQuries
        
        

# Contact Form Serializer
class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = ['id', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
