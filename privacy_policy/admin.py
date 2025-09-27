from django.contrib import admin
from .models import PrivacyPolicy, TrustSafety, TermsConditions, GetInTouch, AboutUs, paymentQuries, AcccountManagement, DataManagement, OurStory
# Register your models here.

@admin.register(PrivacyPolicy)
class PrivacyAndPolicyAdmin(admin.ModelAdmin):
    list_display = ['description']

@admin.register(TrustSafety)
class TrustAndSafetyAdmin(admin.ModelAdmin):
    list_display = ['description']

@admin.register(TermsConditions)
class TermsAndConditionAdmin(admin.ModelAdmin):
    list_display = ['description']
    
@admin.register(GetInTouch)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ['email', 'subject', 'message', 'created_at']
    search_fields = ['email']
    list_filter = ['created_at']
    
    
@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['description']
    
    
@admin.register(paymentQuries)
class paymentQuriesAdmin(admin.ModelAdmin):
    list_display = ['description']
    
@admin.register(AcccountManagement)
class AccountManagementAdmin(admin.ModelAdmin):
    list_display = ['description']
    
@admin.register(DataManagement)
class DataManagementAdmin(admin.ModelAdmin):
    list_display = ['description']
    
@admin.register(OurStory)
class OurStoryAdmin(admin.ModelAdmin):
    list_display = ['description']