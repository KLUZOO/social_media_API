from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from socialmedia.models import Follow
from user.serializers import UserSerializer, UserListSerializer, FollowSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UsersListView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)


class FollowUserView(APIView):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_target_user(self, user_id, current_user_id):
        try:
            target_user_id = int(user_id)
        except (TypeError, ValueError):
            raise ValidationError("Invalid user ID")

        if target_user_id == current_user_id:
            raise ValidationError("You cannot follow yourself.")

        User = get_user_model()
        try:
            return User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")

    def post(self, request, *args, **kwargs):
        target_user = self.get_target_user(kwargs.get("user_id"), request.user.id)

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target_user
        )

        if not created:
            return Response(
                {"detail": "Already following"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        target_user = self.get_target_user(kwargs.get("user_id"), request.user.id)

        try:
            follow = Follow.objects.get(follower=request.user, following=target_user)
            return Response(
                {
                    "detail": f"You've followed {target_user.username} at {follow.created_at}"
                },
                status=status.HTTP_200_OK,
            )
        except Follow.DoesNotExist:
            return Response(
                {"detail": f"You can follow {target_user.username}"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        target_user_id = kwargs.get("user_id")
        try:
            follow = Follow.objects.get(
                follower=request.user, following__id=target_user_id
            )
            follow.delete()
            return Response({"detail": "Unfollowed"}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(
                {"detail": "Not following"}, status=status.HTTP_400_BAD_REQUEST
            )
