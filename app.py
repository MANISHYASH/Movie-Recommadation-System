import streamlit as st
import pickle
import requests

# Function to fetch movie posters
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=bc142f3d54424bf2606973d89b2ba768&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=Error"

# Load movie data and similarity matrix
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
movies_list = movies['title'].values


st.header("🎬 Movie Recommendation System")

# Movie selection
selectvalue = st.selectbox("Select a movie from the dropdown", movies_list)

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    recommend_poster = []
    recommend_release_dates = []
    recommend_genres = []

    for i in distance[1:6]:  # Top 5 recommendations
        movies_id = movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movies_id))

        # Fetch additional details
        movie_details = fetch_movie_details(movies_id)
        recommend_release_dates.append(movie_details.get('release_date', 'N/A'))
        recommend_genres.append(', '.join([genre['name'] for genre in movie_details.get('genres', [])]))

    return recommend_movie, recommend_poster, recommend_release_dates, recommend_genres

# Function to fetch movie details
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=bc142f3d54424bf2606973d89b2ba768&language=en-US"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {}

# Button to show recommendations
if st.button("Show Recommendations"):
    movie_name, movie_poster, release_dates, genres = recommend(selectvalue)
    
    # Displaying the recommended movies in columns
    for idx in range(len(movie_name)):
        with st.expander(movie_name[idx], expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(movie_poster[idx], use_column_width=True)
            with col2:
                st.write(f"**Release Date:** {release_dates[idx]}")
                st.write(f"**Genres:** {genres[idx]}")
                

                # Favorite button
                if st.button(f"Add {movie_name[idx]} to Favorites", key=f"favorite_{idx}"):
                    st.success(f"{movie_name[idx]} added to favorites!")

                # Watchlist button
                if st.button(f"Add {movie_name[idx]} to Watchlist", key=f"watchlist_{idx}"):
                    st.success(f"{movie_name[idx]} added to watchlist!")


