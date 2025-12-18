from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'is_online', 'last_seen', 'posts_count')
    list_filter = ('is_online', 'last_seen')
    search_fields = ('username', 'email')
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Постов'

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context)
