import logging

from django.db import OperationalError
from django.db.utils import ProgrammingError
from api.models import Region

logger = logging.getLogger(__name__)


def get_default_region():
    default_region = None
    try:
        default_region = Region.objects.first()
    except OperationalError as e:
        logger.warning(str(e))
    except ProgrammingError as e:
        logger.warning(str(e))
    return default_region
