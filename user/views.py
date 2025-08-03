from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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


class FollowUserView(generics.CreateAPIView):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            target_user_id = int(kwargs.get("user_id"))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        if target_user_id == request.user.id:
            return Response(
                {"detail": "Cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST
            )

        User = get_user_model()

        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target_user
        )

        if not created:
            return Response(
                {"detail": "Already following"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)


class UnfollowUserView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        target_user_id = kwargs.get("user_id")
        try:
            follow = Follow.objects.get(
                follower=request.user, following__id=target_user_id
            )
            follow.delete()
            return Response({"detail": "Unfollowed"}, status=204)
        except Follow.DoesNotExist:
            return Response({"detail": "Not following"}, status=400)
