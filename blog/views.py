from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Post

def post_list(request):
    posts = Post.objects.filter(status="published").order_by("-created_at")
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog/post_list.html", {"page_obj": page_obj})