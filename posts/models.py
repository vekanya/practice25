from django.conf import settings
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    text = models.TextField("Текст поста")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return f"{self.author.username} - {self.text[:50]}"

    def preview(self, length=250):
        return (self.text[:length] + "...") if len(self.text) > length else self.text

    def likes_count(self):
        return self.reactions.filter(value=1).count()

    def dislikes_count(self):
        return self.reactions.filter(value=-1).count()

    def user_reaction(self, user):
        if not user.is_authenticated:
            return 0
        reaction = self.reactions.filter(user=user).first()
        return reaction.value if reaction else 0


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/%Y/%m/%d/")


class Reaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(LIKE, "Like"), (DISLIKE, "Dislike")])

    class Meta:
        unique_together = ("post", "user")


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
