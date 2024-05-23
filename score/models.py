from django.db import models
from django.utils import timezone

from api.models import Region
from user.models import GameUser


class Score(models.Model):
    id = models.AutoField(primary_key=True)
    score_ts = models.DateTimeField(default=timezone.now)
    points = models.IntegerField()
    user = models.ForeignKey(GameUser,
                             related_name='scores',
                             on_delete=models.CASCADE)

    region = models.ForeignKey(Region, related_name='scores',
                               on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.points}'

