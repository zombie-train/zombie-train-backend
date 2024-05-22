from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Score(models.Model):
    id = models.AutoField(primary_key=True)
    score_ts = models.DateTimeField(default=timezone.now)
    points = models.IntegerField()
    user = models.ForeignKey(User,
                             related_name='scores',
                             on_delete=models.CASCADE)

    region = models.ForeignKey(Region, related_name='scores',
                               on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.points}'
