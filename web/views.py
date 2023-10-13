from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q
from django.http import Http404
from .models import Movie,Myrating
from django.contrib import messages
from .forms import UserForm
from django.db.models import Case, When
from .recommendation import Myrecommend
from random import sample


# for recommendation
import random  # Import the random module

def recommend(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404

    current_user_id = request.user.id  # Get the user's ID

    recommended_movies = Myrecommend(current_user_id) 
    top_6_movies = recommended_movies[:6]
    movie_ids = [item[0] for item in top_6_movies]
    # Query the Movie objects for the selected movie IDs
    movie_list = list(Movie.objects.filter(id__in=movie_ids))

    return render(request, 'web/recommend.html', {'movie_list': movie_list})

def genre_list(request):
    # Fetch a list of unique genres from your Movie model
    genres = Movie.objects.values_list('genre', flat=True).distinct()
    return render(request, 'web/genre_list.html', {'genres': genres})

def movies_in_genre(request, genre):
    # Filter movies by the selected genre
    movies = Movie.objects.filter(genre=genre)
    return render(request, 'web/movies_in_genre.html', {'genre': genre, 'movies': movies})

# List view
def index(request):
	movies = Movie.objects.all()
	movies = sample(list(movies),6)
	movies2 = sample(list(movies),6)
	query  = request.GET.get('q')
	if query:
		movies = Movie.objects.filter(Q(title__icontains=query)).distinct()
		return render(request,'web/query.html',{'movies':movies})
	return render(request,'web/list.html',{'movies':movies,'movies2':movies2})


# detail view
def detail(request, movie_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    movies = get_object_or_404(Movie, id=movie_id)
    
    # For rating
    if request.method == "POST":
        rate = request.POST['rating']
        ratingObject = Myrating()
        ratingObject.user = request.user
        ratingObject.movie = movies
        ratingObject.rating = rate
        ratingObject.save()
        messages.success(request, "Your Rating is submitted")
        return redirect("index")

    return render(request, 'web/detail.html', {'movies': movies})


# Register user
def signUp(request):
	form =UserForm(request.POST or None)
	if form.is_valid():
		user      = form.save(commit=False)
		username  =	form.cleaned_data['username']
		password  = form.cleaned_data['password']
		user.set_password(password)
		user.save()
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
	context ={
		'form':form
	}
	return render(request,'web/signUp.html',context)				


# Login User
def Login(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user     = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return redirect("index")
			else:
				return render(request,'web/login.html',{'error_message':'Your account disable'})
		else:
			return render(request,'web/login.html',{'error_message': 'Invalid Login'})
	return render(request,'web/login.html')

#Logout user
def Logout(request):
	logout(request)
	return redirect("login")




