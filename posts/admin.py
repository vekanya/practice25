from django.contrib import admin
from .models import Comment, Post, PostImage, Reaction

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'text_preview')
    list_filter = ('author', 'created_at')
    inlines = [PostImageInline]
    def text_preview(self, obj):
        return obj.text[:50]

admin.site.register([PostImage, Reaction, Comment])
