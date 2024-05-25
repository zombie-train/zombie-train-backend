from django.urls import path

from score.views import ScoreListCreateView

urlpatterns = [
    path('scores/', ScoreListCreateView.as_view(), name='score-create'),
    # path('leaderboard/', ReadOnlyView.as_view(), name='leaderboard-list-get'),
    # path('my-scores/', ReadOnlyView.as_view(), name='leaderboard-list-get'),
]