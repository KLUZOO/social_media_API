import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
    )

    def __str__(self):
        return (
            f"Post: {self.title}, created at: {self.created_at}, author: {self.author}"
        )


def image_path(instance, filename):
    _, extension = os.path.splitext(filename)
    post_title = getattr(instance.post, "title", "post")
    filename = f"{slugify(post_title)}-{uuid.uuid4()}{extension}"
    return os.path.join("post_images", filename)


class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=image_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} for post {self.post.id}"

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment created at: {self.created_at} by {self.author}"

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    def __str__(self):
        return f"{self.user} liked {self.post.title}"

    class Meta:
        unique_together = ("user", "post")


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} follows {self.following}"

    class Meta:
        unique_together = ("follower", "following")
