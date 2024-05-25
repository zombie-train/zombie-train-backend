from django.urls import path

from score.views import ScoreListCreateView, LeaderboardListView

urlpatterns = [
    path('scores/', ScoreListCreateView.as_view(), name='score-create'),
    path('leaderboard/', LeaderboardListView.as_view(), name='leaderboard-list'),
    # path('my-scores/', ReadOnlyView.as_view(), name='leaderboard-list-get'),
]