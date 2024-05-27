from django.contrib.auth.models import AbstractUser
from django.db import models

from api.models import Region
from api.utils import get_default_region


class GameUser(AbstractUser):
    max_score = models.IntegerField(default=0)
    current_region = models.ForeignKey(Region,
                                       on_delete=models.SET_NULL,
                                       default=get_default_region,
                                       null=True, blank=True,
                                       related_name='current_users')

    def __str__(self):
        return self.username
