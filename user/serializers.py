from django.contrib.auth import get_user_model
from rest_framework import serializers

from socialmedia.models import Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password", "is_staff", "picture", "bio")
        read_only_fields = ("is_staff",)
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


class UserListSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "picture",
            "bio",
            "followers",
        )

    def get_followers(self, obj):
        return [f.follower.username for f in obj.followers.all()]


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = ["id", "created_at", "follower"]
