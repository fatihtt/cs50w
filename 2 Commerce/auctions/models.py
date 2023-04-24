from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=30, blank=True, null=True, unique=True)
    email = models.EmailField(help_text=_('email address'), unique=True)
    def __str__(self):
      return "{}".format(self.email)

class Category(models.Model):
      name = models.CharField(max_length=50)

      def __str__(self):
            return f"{self.id}: {self.name}"

class Listing(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=15, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    ended = models.BooleanField(default=False)

    def __str__(self):
            return f"{self.id}: {self.title}"

    
class Bid(models.Model):
     listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     price = models.DecimalField(max_digits=15, decimal_places=2)
     time = models.DateTimeField(auto_now_add=True, blank=True)
     
     def __str__(self):
            return f"{self.id}: {self.listing.title} : {self.price} : {self.time}"

class WinnerBid(models.Model):
      listing = models.OneToOneField(Listing, on_delete=models.CASCADE)
      bid = models.OneToOneField(Bid, on_delete=models.CASCADE)
     
class Comment(models.Model):
      listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      message = models.TextField()
      time = models.DateTimeField(auto_now_add=True, blank=True)

      def __str__(self):
            return f"{self.id}: {self.listing.title} : {self.user.username} : {self.message}"
      
class Watch(models.Model):
      listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      time = models.DateTimeField(auto_now_add=True, blank=True)

      def __str__(self):
            return f"{self.id}: {self.listing.title} : {self.user.username} : {self.time}"