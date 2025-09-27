from rest_framework import serializers
from .models import Country
from locations.models import Continent

class CountrySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="get_country_code_display", read_only=True)
    
    continent = serializers.PrimaryKeyRelatedField(
        queryset=Continent.objects.all(), required=False, allow_null=True
    )
    
    neighbouring_countries = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        many=True,
        slug_field="country_code",
        required=False
    )
    
    class Meta:
        model = Country
        fields = [
            "country_code",
            "country_logo",
            "country_name",
            "capital",
            "constituent_of",
            "region",
            "continent",
            "official_language",
            "population",
            "status",
            "neighbouring_countries",
        ]
        read_only_fields = ["country_code", "country_name"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["continent"] = instance.continent.name if instance.continent else None
        rep["neighbouring_countries"] = [
            {"code": c.country_code, "name": c.get_country_code_display()}
            for c in instance.neighbouring_countries.all()
        ]
        return rep




class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = ["id", "name", "population", "area_sq_km"]
        read_only_fields = ["id"]


        
# "add_photos", "photos_title",
        
# from locations.models import TravelRecord
# class TravelRecordSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(read_only=True) 

#     class Meta:
#         model = TravelRecord
#         fields = [
#             "id", "user", "country", "visited", "times_visited",
#             "lived_here", "bucket_list", "favourite",
#             "created_at", "updated_at"
#         ]
#         read_only_fields = ["id", "user", "created_at", "updated_at"]

#     def validate(self, attrs):
#         if attrs.get("visited") is False and attrs.get("times_visited", 0) > 0:
#             raise serializers.ValidationError(
#                 "Cannot have times_visited > 0 if not visited."
#             )
#         return attrs

from rest_framework import serializers
from .models import TravelRecord, TravelPhoto, Country

class TravelPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelPhoto
        fields = ["id", "image", "title", "month", "year"]

class TravelRecordSerializer(serializers.ModelSerializer):
    photos = TravelPhotoSerializer(many=True, read_only=True)
    country = serializers.SlugRelatedField(
        queryset=Country.objects.all(),
        slug_field="country_code"
    )

    class Meta:
        model = TravelRecord
        fields = [
            "id",
            "country",
            "visited",
            "times_visited",
            "lived_here",
            "bucket_list",
            "favourite",
            "created_at",
            "updated_at",
            "photos",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def _handle_photos(self, travel_record_or_instance):
        request = self.context.get("request")
        if not request:
            return

        for i in range(1, 4):  # up to 3 photos
            photo = request.FILES.get(f"add_photo_{i}")
            if not photo:
                continue  # skip if not uploaded

            title = request.data.get(f"add_title_{i}", None)
            date = request.data.get(f"add_date_{i}", None)
            month, year = None, None
            if date:
                try:
                    year, month = map(int, date.split("-"))
                except ValueError:
                    pass

            TravelPhoto.objects.create(
                travel_record=travel_record_or_instance,
                image=photo,
                title=title,
                month=month,
                year=year
            )

    def create(self, validated_data):
        request = self.context.get("request")
        travel_record = TravelRecord.objects.create(
            user=request.user,
            **validated_data
        )
        self._handle_photos(travel_record)
        return travel_record

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Delete old photos
        instance.photos.all().delete()
        self._handle_photos(instance)
        return instance




# Feed
# travel/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TravelPhoto

User = get_user_model()


class TravelPhotoFeedSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="travel_record.user.id", read_only=True)
    username = serializers.CharField(source="travel_record.user.username", read_only=True)
    profile_pic = serializers.ImageField(source="travel_record.user.profile_pic", read_only=True)  # assumes User has profile_pic field
    upload_date = serializers.DateTimeField(source="travel_record.created_at", read_only=True)

    class Meta:
        model = TravelPhoto
        fields = ["user_id", "username", "profile_pic", "image", "title", "upload_date"]
