from celery import shared_task
from .models import Post, Tag
from django.contrib.auth import get_user_model
from django.db import transaction


@shared_task
def create_scheduled_post(user_id, title, content, tag_names=None):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    with transaction.atomic():
        post = Post.objects.create(title=title, content=content, author=user)
        if tag_names:
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
            post.save()
