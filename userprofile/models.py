from django.db import models
from account.models import User



class UserProfile(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='profile')
    nickname = models.CharField(max_length=16, unique=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.nickname