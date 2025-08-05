from django.contrib.auth import get_user_model
from rest_framework import serializers

from socialmedia.models import Follow, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "full_name",
            "is_staff",
            "picture",
            "bio",
        )
        read_only_fields = ("is_staff", "full_name")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title")


class UserListSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "picture",
            "bio",
            "followers",
            "following",
            "total_posts",
            "posts",
        )

    def get_followers(self, obj):
        return [f.follower.username for f in obj.followers.all()]

    def get_following(self, obj):
        return [f.following.username for f in obj.following.all()]


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")
        read_only_fields = ("id", "follower", "following", "created_at")
