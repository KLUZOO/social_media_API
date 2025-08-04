from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from social_media_api.permissions import IsAuthorOrReadOnly
from socialmedia.models import Post, PostImage
from socialmedia.serializers import (
    PostListSerializer,
    PostCreateSerializer,
    PostImageSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PostListSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostImageViewSet(viewsets.ModelViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        post_id = self.request.query_params.get("post")
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        post = serializer.validated_data.get("post")
        if post.author != self.request.user:
            raise PermissionDenied("You can only add images to your own posts.")
        serializer.save()
