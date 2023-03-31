from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Movie, Rating, Review
from .forms import MovieForm




def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    reviews = user.review_set.all()
    context = {'user': user, 'reviews': reviews}
    return render(request, 'profile.html', context)

def movie_search(request):
    query = request.GET.get('q')
    if query:
        movies = Movie.objects.filter(title__icontains=query)
    else:
        movies = []
    return render(request, 'movie_search.html', {'movies': movies, 'query': query})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    reviews = Review.objects.filter(movie=movie)
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST['comment']
        review = Review(movie=movie, user=request.user, rating=rating, comment=comment)
        review.save()
        movie.average_rating = Review.objects.filter(movie=movie).aggregate(models.Avg('rating'))['rating__avg']
        movie.save()
    return render(request, 'movies/movie_detail.html', {'movie': movie, 'reviews': reviews})

def movie_management(request):
    if not request.user.is_superuser:
        return redirect('movies:movie_list')
    movies = Movie.objects.all()
    return render(request, 'movies/movie_management.html', {'movies': movies})

def movie_create(request):
    if not request.user.is_superuser:
        return redirect('movies:movie_list')
    form = MovieForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('movies:movie_management')
    return render(request, 'movies/movie_form.html', {'form': form})

def movie_edit(request, movie_id):
    if not request.user.is_superuser:
        return redirect('movies:movie_list')
    movie = get_object_or_404(Movie, pk=movie_id)
    form = MovieForm(request.POST or None, instance=movie)
    if form.is_valid():
        form.save()
        return redirect('movies:movie_management')
    return render(request, 'movies/movie_form.html', {'form': form})

def movie_delete(request, movie_id):
    if not request.user.is_superuser:
        return redirect('movies:movie_list')
    movie = get_object_or_404(Movie, pk=movie_id)
    movie.delete()
    return redirect('movies:movie_management')

def movie_statistics(request):
    top_rated = Movie.objects.order_by('-average_rating')[:10]
    most_reviewed = Movie.objects.annotate(num_reviews=models.Count('review')).order_by('-num_reviews')[:10]
    return render(request, 'movies/movie_statistics.html', {'top_rated': top_rated, 'most_reviewed': most_reviewed})

@login_required
def movie_rating(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user
    rating = None
    review = None
    try:
        rating = Rating.objects.get(movie=movie, user=user)
        review = Review.objects.get(movie=movie, user=user)
    except:
        pass

    if request.method == 'POST':
        rating_value = int(request.POST.get('rating', '0'))
        review_text = request.POST.get('review', '')

        if rating:
            rating.value = rating_value
            rating.save()
        else:
            rating = Rating(movie=movie, user=user, value=rating_value)
            rating.save()

        if review:
            review.text = review_text
            review.save()
        else:
            review = Review(movie=movie, user=user, text=review_text)
            review.save()

        return redirect('movie_detail', movie_id=movie.id)

    context = {
        'movie': movie,
        'rating': rating,
        'review': review,
    }

    return render(request, 'movies/movie_rating.html', context)


@user_passes_test(lambda u: u.is_superuser)
def movie_management(request):
    movies = Movie.objects.annotate(num_ratings=Count('ratings')).order_by('-num_ratings')
    context = {
        'movies': movies,
    }

    return render(request, 'movies/movie_management.html', context)


