from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch

from .models import Country
from .serializers import CountrySerializer

from django.db import transaction


from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


from collections import defaultdict
class CountryListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        sort_by = request.query_params.get("sort", "az")

        # Step 1: Fetch only required fields
        countries = Country.objects.select_related("continent").only(
            "country_code",
            "capital",
            "region",
            "continent__name",
            "official_language",
            "population",
            "status"
        )

        # Step 2: Apply ordering
        if sort_by == "az":
            countries = countries.order_by("country_code")
        elif sort_by == "za":
            countries = countries.order_by("-country_code")
        elif sort_by == "continent":
            countries = countries.order_by("continent__name", "country_code")

        # Step 3: Prepare data
        if sort_by == "continent":
            grouped = defaultdict(list)
            for c in countries:
                continent_name = c.continent.name if c.continent else "Unknown"
                grouped[continent_name].append({
                    "country_code": c.country_code,
                    "country_name": c.get_country_code_display(),
                    "capital": c.capital,
                    "region": c.region,
                    "official_language": c.official_language,
                    "population": c.population,
                    "status": c.status
                })
            return Response({
                "success": True,
                "message": "Countries grouped by continent",
                "data": grouped
            })

        # Flat list (AZ/ZA)
        data = [
            {
                "country_code": c.country_code,
                "country_name": c.get_country_code_display(),
                "capital": c.capital,
                "region": c.region,
                "continent": c.continent.name if c.continent else None,
                "official_language": c.official_language,
                "population": c.population,
                "status": c.status
            }
            for c in countries
        ]

        return Response({
            "success": True,
            "message": "Countries fetched successfully",
            "data": data
        })

class CountryByCodeAPIView(APIView):
    """
    API to fetch a single country by its country_code
    """

    def get(self, request, code):
        try:
            country = get_object_or_404(
                Country.objects.select_related("continent")
                            .prefetch_related("neighbouring_countries"),
                country_code=code
            )
            serializer = CountrySerializer(country)
            return Response({
                'success': True,
                'message': 'Country fetched successfully',
                'data': serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching country with code {code}: {e}")
            return Response(
                {   'success': False,
                    'message': 'No country found with the provided code',
                    "error": "Something went wrong while fetching country data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CountryUpdateAPIView(APIView):
    """Update a country by country_code"""

    def get_object(self, code):
        return get_object_or_404(
            Country.objects.select_related("continent")
                        .prefetch_related("neighbouring_countries"),
            country_code=code
        )

    def put(self, request, code):
        try:
            country = self.get_object(code)
            data = request.data.copy()  # make it mutable

            # Ensure neighbouring_countries is a list if sent as comma string
            if 'neighbouring_countries' in data and isinstance(data['neighbouring_countries'], str):
                data['neighbouring_countries'] = [
                    c.strip().lower() for c in data['neighbouring_countries'].split(',')
                ]

            with transaction.atomic():
                serializer = CountrySerializer(country, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "success": True,
                        "message": "Country information updated successfully",
                        "data": serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "success": False,
                    "message": "Invalid data provided",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error updating country {code}: {e}", exc_info=True)
            return Response({
                "success": False,
                "message": "Something went wrong while updating country"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            



from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import TravelRecord
from accounts.models import UserAuth
from locations.models import Country, Continent
from django.db.models import Sum



# class UserTravelStats(APIView):
#     """
#     API to fetch a user's travel statistics including visited countries,
#     continents, per-continent breakdown, travel summary, and travel lists.
#     """

#     def get(self, request, user_id):
#         try:
#             # Fetch user or return 404
#             user = get_object_or_404(UserAuth, id=user_id)

#             # Check if profile is public or requesting user is the owner
#             if not user.public_profile and request.user != user:
#                 return Response({
#                     'success': False,
#                     'message': 'This profile is private. Access denied.'
#                 }, status=status.HTTP_403_FORBIDDEN)

#             # Fetch all travel records for this user in one query
#             travel_records = (
#                 TravelRecord.objects.filter(user=user)
#                 .select_related("country", "country__continent")
#             )

#             # ===== Countries stats =====
#             total_countries = Country.objects.count()
#             visited_records = [rec for rec in travel_records if rec.visited]
#             visited_countries = len(visited_records)
#             countries_percentage = (
#                 (visited_countries / total_countries * 100) if total_countries else 0.0
#             )

#             # ===== Continents stats =====
#             total_continents = Continent.objects.count()
#             visited_continents = len(
#                 {rec.country.continent_id for rec in visited_records if rec.country.continent_id}
#             )
#             continents_percentage = (
#                 (visited_continents / total_continents * 100) if total_continents else 0.0
#             )

#             # ===== Per-continent breakdown =====
#             per_continent = {}
#             for continent in Continent.objects.all():
#                 total_in_continent = continent.countries.count()
#                 visited_in_continent = sum(
#                     1 for rec in visited_records if rec.country.continent_id == continent.id
#                 )
#                 percentage = (
#                     (visited_in_continent / total_in_continent * 100)
#                     if total_in_continent else 0.0
#                 )
#                 per_continent[continent.name] = {
#                     "visited": visited_in_continent,
#                     "total": total_in_continent,
#                     "percentage": round(percentage, 2),
#                 }

#             # ===== User details =====
#             user_details = {
#                 "full_name": user.get_full_name(),
#                 "email": user.email,
#                 "country_from": user.country.country_name if getattr(user, "country", None) else None,
#                 "lives_in": user.lives_in.country_name if getattr(user, "lives_in", None) else None,
#                 "travel_records_count": travel_records.count(),
#             }

#             # ===== Travel summary =====
#             travel_summary = {
#                 "total_visits": sum(rec.times_visited for rec in visited_records),
#                 "lived_in_count": sum(1 for rec in travel_records if rec.lived_here),
#                 "bucket_list_count": sum(1 for rec in travel_records if rec.bucket_list),
#                 "favorite_count": sum(1 for rec in travel_records if rec.favourite),
#             }

#             # ===== Travel lists =====
#             travel_list_data = {
#                 "visited_countries": [
#                     rec.country.country_code for rec in travel_records if rec.visited
#                 ],
#                 "lived_in_countries": [
#                     rec.country.country_code for rec in travel_records if rec.lived_here
#                 ],
#                 "bucket_list_countries": [
#                     rec.country.country_code for rec in travel_records if rec.bucket_list
#                 ],
#                 "favorite_countries": [
#                     rec.country.country_code for rec in travel_records if rec.favourite
#                 ],
#             }
#             return Response({
#                 "success": True,
#                 "message": "User travel statistics fetched successfully.",
#                 "data": {
#                     "countries": {
#                         "visited": visited_countries,
#                         "total": total_countries,
#                         "percentage": round(countries_percentage, 2),
#                     },
#                     "continents": {
#                         "visited": visited_continents,
#                         "total": total_continents,
#                         "percentage": round(continents_percentage, 2),
#                     },
#                     "per_continent": per_continent,
#                     "user_details": user_details,
#                     "travel_summary": travel_summary,
#                     "travel_lists": travel_list_data,
#                 },
#             }, status=status.HTTP_200_OK)

#         except UserAuth.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": f"No user found with ID {user_id}.",
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             logger.error(f"Error in UserTravelStats API: {str(e)}", exc_info=True)
#             return Response({
#                 "success": False,
#                 "message": "An unexpected server error occurred. Please try again later.",
#                 "details": str(e) if request.user.is_staff else None
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class UserTravelStats(APIView):
    """
    API to fetch a user's travel statistics including visited countries,
    continents, per-continent breakdown, travel summary, and travel lists.
    """

    def get(self, request, user_id):
        try:
            # Fetch user or return 404
            user = get_object_or_404(UserAuth, id=user_id)

            # ===== Sync user's travel records =====
            user.sync_travel_records()

            # Check if profile is public or requesting user is the owner
            if not user.public_profile and request.user != user:
                return Response({
                    'success': False,
                    'message': 'This profile is private. Access denied.'
                }, status=status.HTTP_403_FORBIDDEN)

            # Fetch all travel records for this user in one query
            travel_records = (
                TravelRecord.objects.filter(user=user)
                .select_related("country", "country__continent")
            )

            # ===== Countries stats =====
            total_countries = Country.objects.count()
            visited_records = [rec for rec in travel_records if rec.visited]
            visited_countries = len(visited_records)
            countries_percentage = (
                (visited_countries / total_countries * 100) if total_countries else 0.0
            )

            # ===== Continents stats =====
            total_continents = Continent.objects.count()
            visited_continents = len(
                {rec.country.continent_id for rec in visited_records if rec.country.continent_id}
            )
            continents_percentage = (
                (visited_continents / total_continents * 100) if total_continents else 0.0
            )

            # ===== Per-continent breakdown =====
            per_continent = {}
            for continent in Continent.objects.all():
                total_in_continent = continent.countries.count()
                visited_in_continent = sum(
                    1 for rec in visited_records if rec.country.continent_id == continent.id
                )
                percentage = (
                    (visited_in_continent / total_in_continent * 100)
                    if total_in_continent else 0.0
                )
                per_continent[continent.name] = {
                    "visited": visited_in_continent,
                    "total": total_in_continent,
                    "percentage": round(percentage, 2),
                }

            # ===== User details =====
            user_details = {
                "full_name": user.get_full_name(),
                "email": user.email,
                "country_from": user.country.country_name if getattr(user, "country", None) else None,
                "lives_in": user.lives_in.country_name if getattr(user, "lives_in", None) else None,
                "travel_records_count": travel_records.count(),
            }

            # ===== Travel summary =====
            travel_summary = {
                "total_visits": sum(rec.times_visited for rec in visited_records),
                "lived_in_count": sum(1 for rec in travel_records if rec.lived_here),
                "bucket_list_count": sum(1 for rec in travel_records if rec.bucket_list),
                "favorite_count": sum(1 for rec in travel_records if rec.favourite),
            }

            # ===== Travel lists =====
            travel_list_data = user.travel_lists  # <-- now fully synced

            return Response({
                "success": True,
                "message": "User travel statistics fetched successfully.",
                "data": {
                    "countries": {
                        "visited": visited_countries,
                        "total": total_countries,
                        "percentage": round(countries_percentage, 2),
                    },
                    "continents": {
                        "visited": visited_continents,
                        "total": total_continents,
                        "percentage": round(continents_percentage, 2),
                    },
                    "per_continent": per_continent,
                    "user_details": user_details,
                    "travel_summary": travel_summary,
                    "travel_lists": travel_list_data,
                },
            }, status=status.HTTP_200_OK)

        except UserAuth.DoesNotExist:
            return Response({
                "success": False,
                "message": f"No user found with ID {user_id}.",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error in UserTravelStats API: {str(e)}", exc_info=True)
            return Response({
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
                "details": str(e) if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



            
            
from .serializers import ContinentSerializer

class GetAllContinentsAPIView(APIView):
    def get(self, request):
        try:
            continents = Continent.objects.all().order_by("id")
            serializer = ContinentSerializer(continents, many=True)
            return Response({
                "success": True,
                "message": "Continents fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching continents: {e}")
            return Response({
                "success": False,
                "message": "Something went wrong while fetching continents",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from .serializers import TravelRecordSerializer

class PublicTravelRecordListAPIView(APIView):
    def get(self, request):
        try:
            travel_records = TravelRecord.objects.select_related("user", "country").all()
            serializer = TravelRecordSerializer(travel_records, many=True)
            return Response({
                "success": True,
                "message": "Travel records fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching travel records: {e}")
            return Response({
                "success": False,
                "message": "Something went wrong while fetching travel records",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
        
        
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from .serializers import TravelRecordSerializer
from .models import TravelRecord
import logging

logger = logging.getLogger(__name__)

# class MyTravelRecordCreateAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = TravelRecordSerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     travel_record = serializer.save()
#                 return Response({
#                     "success": True,
#                     "message": "Travel record created successfully",
#                     "data": TravelRecordSerializer(travel_record, context={"request": request}).data
#                 }, status=201)
#             except IntegrityError:
#                 return Response({
#                     "success": False,
#                     "message": "Travel record for this country already exists."
#                 }, status=400)
#             except Exception as e:
#                 logger.error(f"Error creating travel record for user {request.user.id}: {e}")
#                 return Response({
#                     "success": False,
#                     "message": "Something went wrong while creating travel record",
#                     "error": str(e)
#                 }, status=500)
#         return Response({
#             "success": False,
#             "message": "Invalid data provided",
#             "errors": serializer.errors
#         }, status=400)

#     def put(self, request, pk):
#         record = get_object_or_404(TravelRecord, pk=pk, user=request.user)
#         serializer = TravelRecordSerializer(record, data=request.data, context={"request": request})
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     travel_record = serializer.save()
#                 return Response({
#                     "success": True,
#                     "message": "Travel record updated successfully",
#                     "data": TravelRecordSerializer(travel_record, context={"request": request}).data
#                 }, status=200)
#             except Exception as e:
#                 logger.error(f"Error updating travel record {pk} for user {request.user.id}: {e}")
#                 return Response({
#                     "success": False,
#                     "message": "Something went wrong while updating travel record",
#                     "error": str(e)
#                 }, status=500)
#         return Response({
#             "success": False,
#             "message": "Invalid data provided",
#             "errors": serializer.errors
#         }, status=400)



class MyTravelRecordCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TravelRecordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    travel_record = serializer.save()

                    # Sync user's country/lives_in after creating a record
                    request.user.sync_travel_records()

                return Response({
                    "success": True,
                    "message": "Travel record created successfully",
                    "data": TravelRecordSerializer(travel_record, context={"request": request}).data
                }, status=201)
            except IntegrityError:
                return Response({
                    "success": False,
                    "message": "Travel record for this country already exists."
                }, status=400)
            except Exception as e:
                logger.error(f"Error creating travel record for user {request.user.id}: {e}")
                return Response({
                    "success": False,
                    "message": "Something went wrong while creating travel record",
                    "error": str(e)
                }, status=500)

        return Response({
            "success": False,
            "message": "Invalid data provided",
            "errors": serializer.errors
        }, status=400)

    def put(self, request, pk):
        record = get_object_or_404(TravelRecord, pk=pk, user=request.user)
        serializer = TravelRecordSerializer(record, data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    travel_record = serializer.save()

                    # Sync user's country/lives_in after updating a record
                    request.user.sync_travel_records()

                return Response({
                    "success": True,
                    "message": "Travel record updated successfully",
                    "data": TravelRecordSerializer(travel_record, context={"request": request}).data
                }, status=200)
            except Exception as e:
                logger.error(f"Error updating travel record {pk} for user {request.user.id}: {e}")
                return Response({
                    "success": False,
                    "message": "Something went wrong while updating travel record",
                    "error": str(e)
                }, status=500)
        return Response({
            "success": False,
            "message": "Invalid data provided",
            "errors": serializer.errors
        }, status=400)



        
        

from friend_system.views import error_response, success_response
from rest_framework.permissions import AllowAny
from django.db.models import Q       
class SearchCountryAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return error_response(
                message="Query parameter 'q' is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Search in multiple fields: country_code (choices), capital, region
        countries = Country.objects.filter(
            Q(country_code__icontains=query) |
            Q(capital__icontains=query) |
            Q(region__icontains=query) |
            Q(continent__name__icontains=query)
        ).select_related('continent')[:10] 
        
        if not countries.exists():
            return error_response(
                message="No countries found matching the query.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CountrySerializer(countries, many=True)
        return success_response(
            message="Countries fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
        
        
# Feed API
# travel/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import TravelPhoto
from friend_system.models import Follow
from .serializers import TravelPhotoFeedSerializer


class GlobalFeedAPIView(APIView):
    """Returns all travel photos from all users."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        photos = TravelPhoto.objects.select_related(
            "travel_record", "travel_record__user"
        ).order_by("-travel_record__created_at")

        serializer = TravelPhotoFeedSerializer(photos, many=True, context={"request": request})
        return Response({"success": True, "data": serializer.data})


class FriendsFeedAPIView(APIView):
    """Returns travel photos only from friends (mutual follows)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Mutual friends: both sides accepted
        accepted_by = Follow.objects.filter(receiver=user, status="accepted").values_list("requester_id", flat=True)
        accepted_users = Follow.objects.filter(requester=user, status="accepted").values_list("receiver_id", flat=True)

        mutual_friends_ids = set(accepted_by).intersection(set(accepted_users))

        photos = TravelPhoto.objects.select_related(
            "travel_record", "travel_record__user"
        ).filter(travel_record__user_id__in=mutual_friends_ids).order_by("-travel_record__created_at")

        serializer = TravelPhotoFeedSerializer(photos, many=True, context={"request": request})
        return Response({"success": True, "data": serializer.data})
