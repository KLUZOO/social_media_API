from rest_framework import serializers

from socialmedia.models import (
    Post,
    PostImage,
    Like,
    Tag,
    Comment,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "slug", "description", "content", "published")
