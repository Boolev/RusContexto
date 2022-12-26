from django.db import models
from django.utils import timezone


class Room(models.Model):

    name = models.CharField(max_length=30, default='Быстрая игра')

    password = models.CharField(max_length=30, default='')

    created_for_teams = models.BooleanField(default=False)

    secret_word = models.CharField(max_length=50, default='')

    all_guesses = models.TextField(default='')

    similarities = models.TextField(default='')

    guess_counter = models.IntegerField(default=0)

    hint_counter = models.IntegerField(default=0)

    is_victory = models.BooleanField(default=False)

    is_revealed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
