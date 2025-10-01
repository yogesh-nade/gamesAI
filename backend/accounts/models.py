from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended user model for board games platform"""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Gaming stats
    total_games = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_draws = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username
    
    @property
    def win_rate(self):
        """Calculate win rate as percentage"""
        if self.total_games == 0:
            return 0
        return round((self.total_wins / self.total_games) * 100, 2)