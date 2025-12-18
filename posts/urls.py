from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_post_view, name='create'),
    path('<int:pk>/', views.post_detail_view, name='detail'),
    path('<int:pk>/comment/', views.add_comment, name='comment'),
    path('<int:pk>/react/', views.react, name='react'),
]
