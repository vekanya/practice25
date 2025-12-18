# users/admin.py
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_online', 'last_seen', 'posts_count')  # ← добавь
    list_filter = ('is_online', 'last_seen')
    
    def posts_count(self, obj):
        return obj.posts.count()  # ← статистика постов
    posts_count.short_description = 'Постов'

