from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.utils.text import slugify
from django.db import models  # Required for models.Q in PostDetailView

from .models import Post, Category
from .forms import PostForm, RegisterForm


# User Registration
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "blog/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        messages.success(
            self.request,
            "Registration successful! Welcome to DjangoBlog.",
        )
        return response


# Create New Post
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user

        # Create a unique slug
        base_slug = slugify(form.cleaned_data["title"]) or "post"
        slug = base_slug
        counter = 1

        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        form.instance.slug = slug

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Post created successfully!",
        )
        return response

    def get_success_url(self):
        # Published posts open their detail page.
        # Draft posts go to My Posts.
        if self.object.status == "published":
            return reverse_lazy(
                "post_detail",
                kwargs={"slug": self.object.slug},
            )

        return reverse_lazy("my_posts")


# Update Post
class PostUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        post = self.get_object()
        new_slug = slugify(form.cleaned_data["title"]) or "post"

        if new_slug != post.slug:
            slug = new_slug
            counter = 1

            while Post.objects.filter(
                slug=slug
            ).exclude(pk=post.pk).exists():
                slug = f"{new_slug}-{counter}"
                counter += 1

            form.instance.slug = slug

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Post updated successfully!",
        )
        return response

    def get_success_url(self):
        if self.object.status == "published":
            return reverse_lazy(
                "post_detail",
                kwargs={"slug": self.object.slug},
            )

        return reverse_lazy("my_posts")


# Delete Post
class PostDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("home")
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            "Post deleted successfully!",
        )
        return super().form_valid(form)


# Home Page
class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(
            status="published"
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


# My Posts
class MyPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/my_posts.html"
    context_object_name = "posts"
    paginate_by = 6
    login_url = "login"

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user
        ).order_by("-created_at")


# Post Detail
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        # Base queryset: only published posts
        queryset = Post.objects.filter(status="published")
        
        # If the user is authenticated, show published posts OR their own posts (including drafts)
        if self.request.user.is_authenticated:
            queryset = Post.objects.filter(
                models.Q(status="published") | models.Q(author=self.request.user)
            )
            
        return queryset


# About Page
def about(request):
    return render(
        request,
        "blog/about.html",
        {"content": "This is the DjangoBlog team."},
    )


# Contact Page
def contact(request):
    return render(
        request,
        "blog/contact.html",
        {"contact": "This is the Contact Page."},
    )


# Custom 403 Error Page
def custom_403(request, exception=None):
    return render(
        request,
        "blog/403.html",
        status=403,
    )