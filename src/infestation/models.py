from django.db import models
from api.models import Region


class Infestation(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.OneToOneField(
        Region, related_name="infestations", on_delete=models.CASCADE
    )

    start_zombies_count = models.IntegerField(default=100)  # to avoid division by zero

    def __str__(self):
        return f"{self.region.name} - {self.start_zombies_count} zombies"

    def __repr__(self):
        return f"{self.region.name} - {self.start_zombies_count} zombies"
