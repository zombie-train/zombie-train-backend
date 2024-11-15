from django.urls import re_path

from score import views

urlpatterns = [
    re_path('scores/?$', views.ScoreListCreateView.as_view(), name='score-list'),
    re_path('leaderboard/?$', views.LeaderboardListView.as_view(), name='leaderboard-list'),
    re_path('world-map/?$', views.WorldMapView.as_view(), name='worldmap-view'),
    re_path('leaderboard/surrounding/?$', views.SurroundingLeaderboardView.as_view(),
            name='surrounding-leaderboard'),

    # path('my-scores/', ReadOnlyView.as_view(), name='leaderboard-list-get'),
]
