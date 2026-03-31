from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
  email = models.EmailField(unique=True)  
  phone = models.CharField(max_length=15, blank=True, null=True)
  profile_picture = models.ImageField(
    upload_to='profile_pics/', 
    blank=True, 
    null=True
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']  

  class Meta:
    db_table = 'users'
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  def __str__(self):
    return f"{self.username} ({self.email})"