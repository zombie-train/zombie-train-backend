from django.db import models
from django.utils import timezone

from api.models import Region
from zombie_train_backend import settings


class Score(models.Model):
    id = models.AutoField(primary_key=True)
    score_ts = models.DateTimeField(default=timezone.now)
    points = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='scores',
                             on_delete=models.CASCADE)

    region = models.ForeignKey(Region, related_name='scores',
                               on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.points}'

