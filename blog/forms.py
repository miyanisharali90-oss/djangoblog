
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "category",
            "tags",
            "status",
            "cover_image",
        ]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 8, "class": "form-control"}
            ),
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "category": forms.Select(
                attrs={"class": "form-select"}
            ),
            "status": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def clean_title(self):
        title = self.cleaned_data["title"]

        if len(title) < 5:
            raise forms.ValidationError(
                "Title must be at least 5 characters long."
            )

        return title

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        content = cleaned_data.get("content")

        if (
            title
            and content
            and title.lower() in content.lower()[:50]
        ):
            raise forms.ValidationError(
                "Don't repeat the title verbatim at the start "
                "of the content."
            )

        return cleaned_data

    def clean_cover_image(self):
        image = self.cleaned_data.get("cover_image")

        # Allow posts without an image
        if not image:
            return image

        # Maximum image size: 5 MB
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Image file too large (maximum 5MB)."
            )

        # Allowed image extensions
        valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]

        if not any(
            image.name.lower().endswith(ext)
            for ext in valid_extensions
        ):
            raise forms.ValidationError(
                "Unsupported file type. Use JPG, JPEG, PNG, or WEBP."
            )

        return image


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]
