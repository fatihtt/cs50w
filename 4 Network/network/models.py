from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "text": self.text,
            "time": self.time
        }

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

class Fallowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fallowing_user")
    fallower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fallower_user")
    time = models.DateTimeField(auto_now_add=True)
