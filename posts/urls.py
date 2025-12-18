from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.create_post_view, name='create'),
    path('<int:pk>/', views.post_detail_view, name='detail'),
    path('<int:pk>/comment/', views.add_comment_view, name='comment'),
    path('<int:pk>/react/', views.react_view, name='react'), 
]
