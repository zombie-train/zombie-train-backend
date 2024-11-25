from django.contrib.auth.models import AbstractUser
from django.db import models

from api.models import Region
from api.utils import get_default_region
from score.models import Score


class GameUser(AbstractUser):
    max_score = models.IntegerField(default=0)
    current_region = models.ForeignKey(Region,
                                       on_delete=models.SET_NULL,
                                       default=get_default_region,
                                       null=True, blank=True,
                                       related_name='current_users')
    current_region_score = models.ForeignKey(Score,
                                             on_delete=models.SET_NULL,
                                             null=True, blank=True,
                                             related_name='user_current_region_scores')

    is_banned = models.BooleanField(default=False)
    is_cheater = models.BooleanField(default=False)
    is_suspicious = models.BooleanField(default=False)
    current_save = models.TextField(default="")
    referral = models.CharField(max_length=255,
                                default=None,
                                null=True, blank=True)

    def __str__(self):
        return self.username
