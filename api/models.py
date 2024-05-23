from user.models import GameUser
from django.db import models
from django.utils import timezone


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

