from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import date

from api.models import Region
from zombie_train_backend import settings


class Score(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='scores',
                             on_delete=models.CASCADE)

    region = models.ForeignKey(Region,
                               related_name='scores',
                               on_delete=models.CASCADE,
                               )

    score_ts = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.region.name} - {self.value}'


class Leaderboard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='leaderboard_entries')
    region = models.ForeignKey(Region,
                               on_delete=models.CASCADE,
                               related_name='leaderboard_entries')
    score = models.ForeignKey(Score,
                              on_delete=models.CASCADE,
                              related_name='leaderboard_entries')

    score_dt = models.DateField(default=date.today)

    class Meta:
        unique_together = ('user', 'region', 'score_dt')

    def __str__(self):
        return (f"{self.user.username} "
                f"- {self.region.name} "
                f"- {self.score_dt} "
                f"- {self.score.value}")


