from django.urls import path

from score import views

urlpatterns = [
    path('scores/', views.ScoreListCreateView.as_view(), name='score-list'),
    path('leaderboard/', views.LeaderboardListView.as_view(), name='leaderboard-list'),
    path('world-map/', views.WorldMapView.as_view(), name='world-map'),
    # path('my-scores/', ReadOnlyView.as_view(), name='leaderboard-list-get'),
]