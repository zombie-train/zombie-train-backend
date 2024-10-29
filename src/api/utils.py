import logging
from functools import lru_cache
from django.db import OperationalError
from django.db.utils import ProgrammingError
from api.models import Region

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_default_region():
    try:
        return Region.objects.first()
    except OperationalError as e:
        logger.warning(str(e))
    except ProgrammingError as e:
        logger.warning(str(e))
    return None
