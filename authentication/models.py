from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    MALE = "m"
    FEMALE = "f"
    SEX = [(MALE, "Male"),(FEMALE, "Female")]

    sex = models.CharField(max_length=1, choices=SEX, default=MALE)