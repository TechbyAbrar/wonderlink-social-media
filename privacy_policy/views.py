


from rest_framework import generics
from .models import PrivacyPolicy, TrustSafety, TermsConditions, GetInTouch as ContactForm, AboutUs, OurStory, DataManagement, AcccountManagement, paymentQuries
from .serializers import (
    PrivacyPolicySerializer, 
    TrustSafetySerializer, 
    TermsConditionsSerializer,
    ContactFormSerializer,
    AboutUsSerializer,
    OurStorySerializer,
    DataManagementSerializer,
    AcccountManagementSerializer,
    PaymentQueriesSerializer
)
from accounts.permissions import IsSuperUserOrReadOnly
from rest_framework.permissions import AllowAny

class SingleObjectViewMixin:
    def get_object(self):
        return self.queryset.first()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "success": True,
                "message": f"{self.queryset.model.__name__} details retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )
        
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "success": True,
                "message": f"{self.queryset.model.__name__} updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )


class PrivacyPolicyView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = PrivacyPolicy.objects.all()
    serializer_class = PrivacyPolicySerializer
    permission_classes = [IsSuperUserOrReadOnly]

class TrustSafetyView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = TrustSafety.objects.all()
    serializer_class = TrustSafetySerializer
    permission_classes = [IsSuperUserOrReadOnly]

class TermsConditionsView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = TermsConditions.objects.all()
    serializer_class = TermsConditionsSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class AboutUsView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer
    permission_classes = [IsSuperUserOrReadOnly]

class OurStoryView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = OurStory.objects.all()
    serializer_class = OurStorySerializer
    permission_classes = [IsSuperUserOrReadOnly]

class DataManagementView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = DataManagement.objects.all()
    serializer_class = DataManagementSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    
class AcccountManagementView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = AcccountManagement.objects.all()
    serializer_class = AcccountManagementSerializer
    permission_classes = [IsSuperUserOrReadOnly]

class PaymentQueriesView(SingleObjectViewMixin, generics.RetrieveUpdateAPIView):
    queryset = paymentQuries.objects.all()
    serializer_class = PaymentQueriesSerializer
    permission_classes = [IsSuperUserOrReadOnly]




from rest_framework.response import Response
from rest_framework import status
# Get in Touch
class ContactFormView(generics.ListCreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "success": True,
                "message": "Your inquiry has been submitted successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(
            {
                "success": True,
                "message": "Contact form inquiries retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )

class ContactFormDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    permission_classes = [IsSuperUserOrReadOnly]