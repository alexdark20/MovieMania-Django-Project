from django.shortcuts import render
from .models import Movie
from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    description = models.TextField()
    director = models.ForeignKey('Crew', on_delete=models.CASCADE, related_name='directed_movies')
    cast = models.ManyToManyField('Cast', through='Role')
    average_rating = models.FloatField(default=0)

    def __str__(self):
        return self.title

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})


class Cast(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()

    def __str__(self):
        return self.name

class Crew(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()

    def __str__(self):
        return self.name

class Role(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    actor = models.ForeignKey('Cast', on_delete=models.CASCADE)
    character_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.character_name} ({self.actor.name}) in {self.movie.title}"

class Rating(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=2)

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)