from django.contrib import admin

from score.models import Score, Leaderboard

# Register your models here.
admin.site.register(Score)
admin.site.register(Leaderboard)