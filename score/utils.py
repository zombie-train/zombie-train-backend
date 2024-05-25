from .models import Region


def get_default_region():
    return Region.objects.first().id if Region.objects.exists() else None
