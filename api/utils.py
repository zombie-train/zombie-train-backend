from api.models import Region


def get_default_region():
    return Region.objects.first() if Region.objects.exists() else None
