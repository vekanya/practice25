from django.shortcuts import render

# Create your views here.
def home_view(request):

    return render(request, 'posts/home.html')

def create_post_view(request):

    return render(request, 'posts/create_post.html')

def post_page_view(request):

    return render(request, 'posts/post.html')