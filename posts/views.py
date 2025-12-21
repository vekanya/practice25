from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from users.models import User
from .forms import PostForm, CommentForm
from .models import Post, PostImage, Reaction
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import UntypedToken


def home_view(request):
    query = request.GET.get("q", "").strip()

    if query:
        posts = (
            Post.objects.filter(
                Q(text__icontains=query) | Q(author__username__icontains=query)
            )
            .select_related("author")
            .prefetch_related("images", "comments__author", "reactions")[:20]
        )
    else:
        posts = Post.objects.select_related("author").prefetch_related(
            "images", "comments__author", "reactions"
        )[:20]

    return render(request, "posts/home.html", {"posts": posts, "query": query})


def create_post_view(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if not text:
            form = PostForm()
            return render(request, "posts/create_post.html", {"form": form})

        post = Post.objects.create(author=request.user, text=text)

        for image_file in request.FILES.getlist("images"):
            PostImage.objects.create(post=post, image=image_file)

        return redirect("posts:home")

    form = PostForm()
    return render(request, "posts/create_post.html", {"form": form})


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related(
            "images", "comments__author"
        ),
        pk=pk,
    )
    return render(request, "posts/post.html", {"post": post})


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_comment_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

        comment_data = {
            "id": comment.id,
            "author_id": comment.author.id,
            "author_username": comment.author.username,
            "author_avatar": (
                comment.author.avatar.url
                if comment.author.avatar
                else "/static/images/default_avatar.jpg"
            ),
            "text": comment.text,
        }
        return JsonResponse({"success": True, "comment": comment_data})
    else:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def react_view(request, pk):

    user = None
    if request.user.is_authenticated and hasattr(request.user, 'id'):
        user = request.user
    else:

        user = User.objects.first()
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)
    
    user = request.user
    post = get_object_or_404(Post, pk=pk)
    value_str = request.POST.get("value")
    value = 1 if value_str == "like" else -1

    reaction, created = Reaction.objects.get_or_create(
        post=post, user=user, defaults={"value": value}
    )

    if not created and reaction.value == value:
        reaction.delete()
    elif not created:
        reaction.value = value
        reaction.save()

    likes_count = Reaction.objects.filter(post=post, value=1).count()
    dislikes_count = Reaction.objects.filter(post=post, value=-1).count()
    
    user_reaction = Reaction.objects.filter(post=post, user=user).first()
    user_reaction = user_reaction.value if user_reaction else 0

    return JsonResponse({
        "likes": likes_count,
        "dislikes": dislikes_count,
        "user_reaction": user_reaction,
    })


