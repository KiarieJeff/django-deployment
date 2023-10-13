import pandas as pd
from web.models import Myrating,Movie
from surprise.prediction_algorithms import SVD
from surprise import Reader, Dataset


def Myrecommend(user_id):
    # Get user's rated movies
    rated_movies = Myrating.objects.filter(user_id=user_id).values_list('movie_id', flat=True)
    
    # Create a list of all movies available in the dataset
    all_movies = Movie.objects.values_list('id', flat=True).distinct()
    
    # Find movies that the user has not rated
    unrated_movies = list(set(all_movies) - set(rated_movies))
    
    # Create a DataFrame with unrated movies
    new_df = pd.DataFrame({
        'user_id': [user_id] * len(unrated_movies),
        'movie_id': unrated_movies,
        'rating': [0] * len(unrated_movies)  # You can initialize with a default rating value
    })
    
    reader = Reader(rating_scale=(1, 5))
    new_data = Dataset.load_from_df(new_df, reader)
    
    svd = SVD(n_factors=20, reg_all=0.02)
    svd.fit(new_data.build_full_trainset())
    
    list_of_movies = []
    
    for m_id in new_df['movie_id'].unique():
        prediction = svd.predict(user_id, m_id)
        list_of_movies.append((m_id, prediction.est)) 
    
    ranked_movies = sorted(list_of_movies, key=lambda x: x[1], reverse=True)
    return ranked_movies







