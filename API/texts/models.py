from django.db import models
from accounts.models import User

# from django.contrib.auth.models import User


# Create your models here.
class Text(models.Model):
    user_input = models.CharField(max_length=2048)
    chatgpt_input = models.CharField(max_length=2048, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_column="timestamp")
    updated_at = models.DateTimeField(auto_now=True)
