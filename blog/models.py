
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from PIL import Image, UnidentifiedImageError


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    cover_image = models.ImageField(
        upload_to="post_covers/",
        blank=True,
        null=True,
    )

    content = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="published",
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically generate a unique slug
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            slug = base_slug
            counter = 1

            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Save the post first so the uploaded image exists
        super().save(*args, **kwargs)

        # Resize cover image while preserving aspect ratio
        if self.cover_image:
            try:
                with Image.open(self.cover_image.path) as img:
                    img.thumbnail((800, 800))
                    img.save(self.cover_image.path)

            except (
                OSError,
                ValueError,
                UnidentifiedImageError,
            ):
                pass

    def __str__(self):
        return self.title
