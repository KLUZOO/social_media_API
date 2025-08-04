from django.db import transaction
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


class PostListSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "tags",
            "created_at",
            "images",
            "total_comments",
            "total_likes",
        )
        read_only_fields = ("id", "created_at", "images")

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_images(self, obj):
        request = self.context.get("request")
        urls = []
        for image in obj.images.all():
            if image.image:
                url = image.image.url
                if request is not None:
                    url = request.build_absolute_uri(url)
                urls.append(url)
        return urls


class PostCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = ("id", "title", "content", "tags", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        with transaction.atomic():
            post = Post.objects.create(**validated_data)
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
            return post


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "post", "image", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_post(self, value):
        request = self.context.get("request")
        if request and value.author != request.user:
            raise serializers.ValidationError(
                "You can only add images to your own posts."
            )
        return value
