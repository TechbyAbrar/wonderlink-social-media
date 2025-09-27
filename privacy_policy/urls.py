from django.urls import path
from .views import (
    PrivacyPolicyView,
    TrustSafetyView,
    TermsConditionsView, ContactFormView, ContactFormDetailView,
    AboutUsView,
    OurStoryView,
    DataManagementView,
    AcccountManagementView,
    PaymentQueriesView,
)

urlpatterns = [
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('trust-safety/', TrustSafetyView.as_view(), name='trust-safety'),
    path('terms-conditions/', TermsConditionsView.as_view(), name='terms-conditions'),
    path('contact-form/', ContactFormView.as_view(), name='contact-form'),
    path('contact-form/<int:pk>/', ContactFormDetailView.as_view(), name='contact-form'),
    path("about-us/", AboutUsView.as_view(), name="about-us"),
    path("our-story/", OurStoryView.as_view(), name="our-story"),
    path("data-management/", DataManagementView.as_view(), name="data-management"),
    path("account-management/", AcccountManagementView.as_view(), name="account-management"),
    path("payment-queries/", PaymentQueriesView.as_view(), name="payment-queries"),
]
