from user.models import GameUser
from api.models import Region
from score.models import Score

def create_test_user(username='testuser', password='testpass123'):
    """Create a test user"""
    return GameUser.objects.create_user(
        username=username,
        password=password
    )

def create_test_data(user):
    """Create test region and score for a user"""
    region = Region.objects.create(name='Test Region')
    score = Score.objects.create(
        user=user,
        region=region,
        value=100
    )
    user.current_region = region
    user.current_region_score = score
    user.save()
    return region, score