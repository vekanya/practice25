from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.create_post_view, name='create'),
    path('post/', views.post_page_view, name='post'),
]
