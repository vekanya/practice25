from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from .forms import PostForm, CommentForm
from .models import Post, PostImage, Reaction

def home(request):
    posts = Post.objects.select_related('author').prefetch_related(
        'images', 'comments__author', 'reactions'
    )[:10]
    return render(request, 'posts/home.html', {'posts': posts})

@login_required
def create_post_view(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text:
            form = PostForm()
            return render(request, 'posts/create_post.html', {'form': form})
        
        post = Post.objects.create(author=request.user, text=text)
        
        # Сохраняем изображения
        for image_file in request.FILES.getlist('images'):
            PostImage.objects.create(post=post, image=image_file)
        
        return redirect('posts:home')
    
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_detail_view(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related('images', 'comments__author'),
        pk=pk
    )
    return render(request, 'posts/post.html', {'post': post})  # ← post.html вместо detail.html


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('posts:home')
    return redirect('posts:home')

@login_required
def react(request, pk):
    post = get_object_or_404(Post, pk=pk)
    value = 1 if request.POST.get('value') == 'like' else -1
    
    reaction, created = Reaction.objects.get_or_create(
        post=post, user=request.user,
        defaults={'value': value}
    )
    
    if not created and reaction.value == value:
        reaction.delete()
    else:
        reaction.value = value
        reaction.save()
    
    return JsonResponse({
        'likes': post.likes_count(),
        'dislikes': post.dislikes_count(),
        'user_reaction': post.user_reaction(request.user)
    })
