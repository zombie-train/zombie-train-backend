from django.db import models
from django.contrib.auth.models import User


class Score(models.Model):
    id = models.AutoField(primary_key=True)
    score_ts = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField()
    user = models.ForeignKey(User,
                             related_name='scores',
                             on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.points}'
