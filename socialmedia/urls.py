from django.urls import path, include
from rest_framework import routers

from socialmedia.views import PostViewSet, PostImageViewSet, CommentDeleteViewSet

router = routers.DefaultRouter()
router.register("posts", PostViewSet)
router.register("post-images", PostImageViewSet, basename="post-image")
router.register("destroy-comment", CommentDeleteViewSet, basename="destroy-comment")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "social_media"
