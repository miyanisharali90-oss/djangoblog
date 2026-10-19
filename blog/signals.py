
import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Post


@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if not instance.cover_image:
        return

    image_path = instance.cover_image.path

    # Do not delete an image that another post uses
    other_posts = Post.objects.filter(
        cover_image=instance.cover_image.name
    ).exclude(pk=instance.pk)

    if not other_posts.exists() and os.path.isfile(image_path):
        try:
            os.remove(image_path)
        except OSError:
            pass
