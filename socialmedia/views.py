from datetime import datetime

from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media_api.permissions import IsAuthorOrReadOnly
from socialmedia.models import Post, PostImage, Comment, Like
from socialmedia.serializers import (
    PostListSerializer,
    PostCreateSerializer,
    PostImageSerializer,
    PostRetrieveSerializer,
    CommentSerializer,
    ScheduledPostSerializer,
)
from django.utils.timezone import now
from .tasks import create_scheduled_post


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        request = self.request
        queryset = self.queryset.all()

        title = request.query_params.get("title")
        content = request.query_params.get("content")
        author = request.query_params.get("author")
        created_after = request.query_params.get("created_after")
        created_before = request.query_params.get("created_before")
        follower = request.query_params.get("follower")
        following = request.query_params.get("following")
        tags = request.query_params.get("tags")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if content:
            queryset = queryset.filter(content__icontains=content)

        if author:
            queryset = queryset.filter(
                Q(author__username__icontains=author)
                | Q(author__first_name__icontains=author)
                | Q(author__last_name__icontains=author)
            )

        if created_after:
            dt = parse_datetime(created_after)
            if dt:
                queryset = queryset.filter(created_at__gte=dt)

        if created_before:
            dt = parse_datetime(created_before)
            if dt:
                queryset = queryset.filter(created_at__lte=dt)

        if follower == "true":
            queryset = queryset.filter(author__followers__follower=request.user)
        elif follower == "false":
            queryset = queryset.exclude(author__followers__follower=request.user)

        if following == "true":
            queryset = queryset.filter(author__following__following=request.user)
        elif following == "false":
            queryset = queryset.exclude(author__following__following=request.user)

        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            queryset = queryset.filter(tags__name__in=tag_list).distinct()

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        elif self.action == "comment":
            return CommentSerializer
        elif self.action == "scheduled_post":
            return ScheduledPostSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if not created:
            return Response(
                {"detail": "You have already liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Post liked successfully."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        try:
            like = Like.objects.get(post=post, user=request.user)
            like.delete()
            return Response(
                {"detail": "Like removed successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Like.DoesNotExist:
            return Response(
                {"detail": "You have not liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=["post"],
        url_path="schedule",
        permission_classes=[IsAuthenticated],
    )
    def schedule_post(self, request):
        serializer = ScheduledPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        schedule_time = data["scheduled_time"]
        delay = (schedule_time - now()).total_seconds()

        if delay <= 0:
            return Response(
                {"detail": "scheduled_time must be in the future"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_scheduled_post.apply_async(
            args=[
                request.user.id,
                data["title"],
                data["content"],
                data.get("tags", []),
            ],
            countdown=delay,
        )

        return Response(
            {"detail": "Post scheduled successfully"}, status=status.HTTP_202_ACCEPTED
        )


class CommentDeleteViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            raise PermissionDenied("You do not have permission to delete this comment")
        return super().destroy(request, *args, **kwargs)


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
