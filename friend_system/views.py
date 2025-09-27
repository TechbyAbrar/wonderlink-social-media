from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Follow
from accounts.models import UserAuth
from .serializers import FollowSerializer
from accounts.serializers import UserSerializer
from django.db.models import Q

# --- Standard response helpers ---
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



# # --- Send follow request ---
# class SendFollowRequestAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         followed_id = request.data.get('followed_id')
#         if not followed_id:
#             return error_response("followed_id is required")

#         try:
#             followed_user = UserAuth.objects.get(id=followed_id)
#         except UserAuth.DoesNotExist:
#             return error_response("User not found", status.HTTP_404_NOT_FOUND)

#         try:
#             follow_obj = Follow.send_request(follower=request.user, followed=followed_user)
#         except ValueError as e:
#             return error_response(str(e), status.HTTP_400_BAD_REQUEST)

#         return success_response(
#             "Follow request sent successfully",
#             FollowSerializer(follow_obj).data,
#             status.HTTP_201_CREATED
#         )


# # --- Accept follow request ---
# class AcceptFollowRequestAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, follow_id):
#         try:
#             follow_obj = Follow.objects.get(id=follow_id, followed_id=request.user.id, status='pending')
#         except Follow.DoesNotExist:
#             return error_response("Follow request not found", status.HTTP_404_NOT_FOUND)

#         follow_obj.accept()
#         return success_response("Follow request accepted", FollowSerializer(follow_obj).data)


# # --- Reject follow request ---
# class RejectFollowRequestAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, follow_id):
#         try:
#             follow_obj = Follow.objects.get(id=follow_id, followed_id=request.user.id, status='pending')
#         except Follow.DoesNotExist:
#             return error_response("Follow request not found", status.HTTP_404_NOT_FOUND)

#         follow_obj.reject()
#         return success_response("Follow request rejected", FollowSerializer(follow_obj).data)


# class FollowBackAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, follow_id):
#         """
#         Accept a pending follow request (followback) by follow_id for the logged-in user.
#         """
#         try:
#             # Ensure the follow request exists and is pending for this user
#             follow_obj = Follow.objects.select_related('follower', 'followed').get(
#                 id=follow_id,
#                 followed_id=request.user.id,
#                 status='pending'
#             )
#         except Follow.DoesNotExist:
#             return error_response("Follow request not found", status.HTTP_404_NOT_FOUND)

#         # Call a method to accept the follow request
#         follow_obj.status = 'accepted'
#         follow_obj.save()

#         # Optional: You can automatically create a reciprocal follow if your app requires
#         if not Follow.objects.filter(follower=request.user, followed=follow_obj.follower).exists():
#             Follow.objects.create(follower=request.user, followed=follow_obj.follower, status='accepted')

#         return success_response(
#             "Followed back successfully",
#             FollowSerializer(follow_obj).data
#         )


# # --- List followers ---
# class FollowersListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id):
#         try:
#             user = UserAuth.objects.get(id=user_id)
#         except UserAuth.DoesNotExist:
#             return error_response("User not found", status.HTTP_404_NOT_FOUND)

#         followers = user.followers.filter(status='accepted').select_related('follower')
#         serialized_data = [
#             {
#                 "id": f.follower.id,
#                 "email": f.follower.email,
#                 "name": f.follower.get_full_name(),
#                 "profile_pic": f.follower.profile_pic.url if f.follower.profile_pic else None,
#             }
#             for f in followers
#         ]
#         return success_response("Followers fetched successfully", serialized_data)


# # --- List following ---
# class FollowingListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id):
#         try:
#             user = UserAuth.objects.get(id=user_id)
#         except UserAuth.DoesNotExist:
#             return error_response("User not found", status.HTTP_404_NOT_FOUND)

#         following = user.following.filter(status='accepted').select_related('followed')
#         serialized_data = [
#             {
#                 "id": f.followed.id,
#                 "email": f.followed.email,
#                 "name": f.followed.get_full_name(),
#                 "profile_pic": f.followed.profile_pic.url if f.followed.profile_pic else None,
#             }
#             for f in following
#         ]
#         return success_response("Following list fetched successfully", serialized_data)







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserAuth
from .models import Follow
from .serializers import FollowSerializer


# --- Helpers ---
def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({"success": True, "message": message, "data": data}, status=status_code)


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "message": message, "data": None}, status=status_code)


# --- Send follow request ---
class SendFollowRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get("receiver_id")
        if not receiver_id:
            return error_response("receiver_id is required")

        try:
            receiver = UserAuth.objects.get(id=receiver_id)
        except UserAuth.DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        try:
            follow_obj = Follow.send_request(requester=request.user, receiver=receiver)
        except ValueError as e:
            return error_response(str(e))

        return success_response(
            "Follow request sent",
            FollowSerializer(follow_obj).data,
            status.HTTP_201_CREATED,
        )


# --- Accept follow request ---
class AcceptFollowRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, follow_id):
        try:
            follow_obj = Follow.objects.get(id=follow_id, receiver=request.user, status="pending")
        except Follow.DoesNotExist:
            return error_response("Follow request not found", status.HTTP_404_NOT_FOUND)

        follow_obj.accept()
        return success_response("Follow request accepted", FollowSerializer(follow_obj).data)


# --- Reject follow request ---
class RejectFollowRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, follow_id):
        try:
            follow_obj = Follow.objects.get(id=follow_id, receiver=request.user, status="pending")
        except Follow.DoesNotExist:
            return error_response("Follow request not found", status.HTTP_404_NOT_FOUND)

        follow_obj.reject()
        return success_response("Follow request rejected", FollowSerializer(follow_obj).data)


# --- Follow back ---
# class FollowBackAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, follow_id):
#         try:
#             follow_obj = Follow.objects.get(id=follow_id, receiver=request.user, status="pending")
#         except Follow.DoesNotExist:
#             return error_response("Follow request not found", status.HTTP_404_NOT_FOUND)

#         follow_obj.followback()
#         return success_response("Followed back successfully", FollowSerializer(follow_obj).data)


class FollowBackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        # Check if a follow request exists from them -> me
        follow_obj, created = Follow.objects.get_or_create(
            requester_id=user_id,
            receiver=request.user,
            defaults={"status": "accepted"}
        )

        if not created and follow_obj.status != "accepted":
            follow_obj.status = "accepted"
            follow_obj.save()

        # Ensure I follow them back
        reciprocal, created = Follow.objects.get_or_create(
            requester=request.user,
            receiver_id=user_id,
            defaults={"status": "accepted"}
        )
        if not created and reciprocal.status != "accepted":
            reciprocal.status = "accepted"
            reciprocal.save()

        return success_response(
            "Followed back successfully",
            {"follower_id": user_id, "mutual": True}
        )


# --- List followers ---
class FollowersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = UserAuth.objects.get(id=user_id)
        except UserAuth.DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        followers = user.followers.filter(status="accepted").select_related("requester")
        serialized = [
            {
                "id": f.requester.id,
                "email": f.requester.email,
                "full_name": f.requester.full_name,
                "profile_pic": f.requester.profile_pic.url if f.requester.profile_pic else None,
            }
            for f in followers
        ]
        return success_response("Followers list", serialized)


# --- List following ---
class FollowingListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = UserAuth.objects.get(id=user_id)
        except UserAuth.DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        following = user.following.filter(status="accepted").select_related("receiver")
        serialized = [
            {
                "id": f.receiver.id,
                "email": f.receiver.email,
                "full_name": f.receiver.full_name,
                "profile_pic": f.receiver.profile_pic.url if f.receiver.profile_pic else None,
            }
            for f in following
        ]
        return success_response("Following list", serialized)


# --- Pending requests ---
# class PendingFollowRequestsAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         pending = Follow.objects.filter(receiver=request.user, status="pending").select_related("requester")
#         serialized = [
#             {
#                 "follow_id": f.id,
#                 "requester_id": f.requester.id,
#                 "requester_name": f.requester.full_name,
#                 "requester_email": f.requester.email,
#                 "profile_pic": f.requester.profile_pic.url if f.requester.profile_pic else None,
#                 "requested_at": f.created_at,
#             }
#             for f in pending
#         ]
#         return success_response("Pending follow requests", serialized)











# --- Profile view (mutual follow check) ---
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            target_user = UserAuth.objects.get(id=user_id)
        except UserAuth.DoesNotExist:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        if target_user == request.user or target_user.can_view_profile(request.user):
            serialized_data = UserSerializer(target_user).data
            return success_response("Profile fetched successfully", serialized_data)

        return error_response("You cannot view this profile", status.HTTP_403_FORBIDDEN)




# --- Search User API ---
class SearchUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()

        if not query:
            return error_response(
                message="Query parameter 'q' is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            users = UserAuth.objects.filter(
                Q(email__icontains=query) |
                Q(username__icontains=query) |
                Q(full_name__icontains=query)
            )

            if not users.exists():
                return success_response(
                    message="No users found matching your query",
                    data=[]
                )

            serialized_data = UserSerializer(users, many=True).data

            return success_response(
                message="Users fetched successfully",
                data=serialized_data
            )

        except Exception as e:
            return error_response(
                message=f"An error occurred while searching users: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Report and Block API Section
import logging
from django.core.cache import cache
from rest_framework import status
from django.db.models import Q

from .models import Report, Block
from .serializers import ReportSerializer, BlockSerializer

logger = logging.getLogger(__name__)


class ReportUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReportSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            report = serializer.save()
            logger.info(f"User {request.user.id} reported {report.reported_user.id}")
            return Response({
                "success":True,
                "detail": "Report submitted successfully."}, status=status.HTTP_201_CREATED)
        logger.warning(f"Report failed: {serializer.errors}")
        return Response({
            "success":False,
            "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class BlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BlockSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            block, created = Block.objects.get_or_create(
                blocker=request.user,
                blocked_user=serializer.validated_data["blocked_user"]
            )
            if created:
                logger.info(f"User {request.user.id} blocked {block.blocked_user.id}")
                return Response({"success":True, "detail": "User blocked successfully."}, status=status.HTTP_201_CREATED)
            return Response({"detail": "User already blocked."}, status=status.HTTP_200_OK)
        logger.warning(f"Block failed: {serializer.errors}")
        return Response({
            "success":False,
            "detail": "User already blocked and you can not block yourself.",
            "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        blocked_user_id = request.data.get("blocked_user")
        if not blocked_user_id:
            return Response({"error": "blocked_user is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            block = Block.objects.get(blocker=request.user, blocked_user_id=blocked_user_id)
            block.delete()
            logger.info(f"User {request.user.id} unblocked {blocked_user_id}")
            return Response({"detail": "User unblocked successfully."}, status=status.HTTP_200_OK)
        except Block.DoesNotExist:
            return Response({"detail": "No block found."}, status=status.HTTP_404_NOT_FOUND)



class BlockListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch blocked users with select_related to avoid extra queries
            blocks = Block.objects.filter(blocker=request.user).select_related("blocked_user")
            serializer = BlockSerializer(blocks, many=True, context={"request": request})

            return success_response("Blocked users fetched successfully", serializer.data)

        except Exception as e:
            return error_response(str(e))



from .serializers import FollowerRequestSerializer

# class PendingFollowRequestsAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         pending_requests = Follow.objects.filter(
#             followed_id=request.user.id,
#             status='pending'
#         ).select_related('follower')  # avoid N+1 queries

#         serialized_data = [
#             {
#                 "follow_id": f.id,
#                 "follower_id": f.follower.id,
#                 "follower_name": f.follower.get_full_name(),
#                 "follower_email": f.follower.email,
#                 "profile_pic": f.follower.profile_pic.url if f.follower.profile_pic else None,
#                 "requested_at": f.created_at
#             }
#             for f in pending_requests
#         ]

#         return success_response(
#             "Pending follow requests fetched successfully",
#             serialized_data
#         )

class PendingFollowRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending_requests = Follow.objects.filter(
            receiver_id=request.user.id,   # FIXED: use receiver_id instead of followed_id
            status='pending'
        ).select_related('requester')  # FIXED: use requester instead of follower

        serialized_data = [
            {
                "follow_id": f.id,
                "requester_id": f.requester.id,  # requester = who sent the request
                "requester_name": f.requester.get_full_name(),
                "requester_email": f.requester.email,
                "profile_pic": f.requester.profile_pic.url if f.requester.profile_pic else None,
                "requested_at": f.created_at
            }
            for f in pending_requests
        ]

        return success_response(
            "Pending follow requests fetched successfully",
            serialized_data
        )
        
        
        

from .serializers import FriendTravelSerializer

class FriendsListAPIView(APIView):
    """
    Returns a list of mutual friends with their travel stats:
    visited, lived_in, bucket_list, favourite.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            # Mutual friends: both sides accepted
            accepted_by = Follow.objects.filter(receiver=user, status="accepted").values_list("requester_id", flat=True)
            accepted_users = Follow.objects.filter(requester=user, status="accepted").values_list("receiver_id", flat=True)
            mutual_ids = set(accepted_by).intersection(set(accepted_users))

            if not mutual_ids:
                return Response({
                    "success": True,
                    "message": "No mutual friends found.",
                    "data": []
                })

            # Only include friends who allow public profile
            friends_qs = UserAuth.objects.filter(id__in=mutual_ids, public_profile=True)
            serializer = FriendTravelSerializer(friends_qs, many=True)

            return Response({
                "success": True,
                "message": "Friends list fetched successfully.",
                "data": serializer.data
            })

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Failed to fetch friends list: {str(e)}",
                "data": []
            }, status=500)