# Generated by Django 4.2.16 on 2024-10-29 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0010_score_score_score_value_36f182_idx'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='leaderboard',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='leaderboard',
            constraint=models.UniqueConstraint(fields=('user_id', 'region_id', 'score_dt'), name='unique_user_region_date'),
        ),
    ]
