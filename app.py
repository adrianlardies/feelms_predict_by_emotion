import mysql.connector
import streamlit as st
import pandas as pd
import datetime
import random
import pickle
import os
from dotenv import load_dotenv

st.set_page_config(
    page_title="Feelms - Predicting by Emotion",
    page_icon="🎬",  # Puedes cambiar el icono
    layout="centered",  # 'centered' o 'wide' dependiendo del diseño que prefieras
    initial_sidebar_state="expanded",  # El sidebar estará expandido por defecto
)

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

# Connect to MySQL database using the loaded environment variables
conn = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name,
    port=db_port,
    auth_plugin='caching_sha2_password'
)
c = conn.cursor()

# Load pre-trained models from pickle files
with open('model/svd_model.pkl', 'rb') as file:
    svd_model = pickle.load(file)

with open('model/rf_model.pkl', 'rb') as file:
    rf_model = pickle.load(file)

# Function to predict movie rating using the SVD model
def predict_rating(user_id, movie_id):
    # Generate the prediction using the SVD model
    try:
        pred = svd_model.predict(user_id, movie_id)
        return pred.est  # Return the predicted rating
    except:
        return 5  # Default value if no prediction is available

# Function to predict if a movie will be marked as favorite using RandomForest
def predict_favorite(features):
    # Use the RandomForest model to predict whether the movie will be marked as favorite
    prediction = rf_model.predict([features])
    return prediction[0]

# Function to check if the user exists or create a new one
def get_or_create_user(username, password):
    query = "SELECT user_id FROM users WHERE username = %s"
    c.execute(query, (username,))
    result = c.fetchone()

    if not result:
        # If the user doesn't exist, create a new one with the provided password
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        c.execute(query, (username, password))
        conn.commit()
        st.success(f"User {username} has been created.")
        return c.lastrowid  # Return the new user's ID (user_id)
    else:
        # If the user exists, validate the password
        query = "SELECT user_id FROM users WHERE username = %s AND password = %s"
        c.execute(query, (username, password))
        result = c.fetchone()
        if result:
            st.success(f"Welcome back, {username}!")
            return result[0]  # Return the existing user's ID (user_id)
        else:
            st.error("Incorrect password. Please try again.")
            return None

# Function to handle user session state
def login(username, password):
    user_id = get_or_create_user(username, password)
    if user_id:
        st.session_state['user_id'] = user_id
        st.session_state['username'] = username
        st.session_state['logged_in'] = True
        st.rerun()

# Function to log out
def logout():
    st.session_state.clear()  # Clear the entire session
    st.success("You have successfully logged out.")
    st.rerun()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None

# If the user is not logged in, show the login/registration form
if not st.session_state['logged_in']:
    st.title("🎬 Feelms - Predicting by Emotion")

    # Request the username
    username = st.text_input("Username")

    # Request the password
    password = st.text_input("Password", type="password")

    # Button to log in or register
    if st.button("Login / Register"):
        if username and password:
            login(username, password)
else:
    st.write(f"Welcome, {st.session_state['username']}!")

    # Logout button
    if st.button("Logout"):
        logout()

    # Save interactions in the database using the DataFrame index as movie_id
    def save_interaction(user_id, movie_id, emotion, interaction_type):
        query = "INSERT INTO interactions (user_id, movie_id, emotion, interaction_type, date) VALUES (%s, %s, %s, %s, %s)"
        values = (user_id, movie_id, emotion, interaction_type, datetime.datetime.now())
        c.execute(query, values)
        conn.commit()

    # Check if the movie has already been shown in the current session
    def check_session_interaction(movie_id):
        if 'shown_movies' not in st.session_state:
            st.session_state['shown_movies'] = set()  # Use a set to avoid duplicates in the session
        
        # Check if the movie has already been shown in this session
        return movie_id in st.session_state['shown_movies']
    
    # Register the movie as shown in the current session
    def register_session_interaction(movie_id):        
        st.session_state['shown_movies'].add(movie_id)

    # Function to update an existing interaction in the database
    def update_interaction(user_id, movie_id, interaction_type):
        query = """
        UPDATE interactions 
        SET interaction_type = %s, date = %s 
        WHERE user_id = %s AND movie_id = %s AND interaction_type = 'shown'
        """
        values = (interaction_type, datetime.datetime.now(), user_id, movie_id)
        c.execute(query, values)
        conn.commit()

    # Function to save favorites
    def save_favorite(user_id, movie_id):
        query = "SELECT * FROM favorites WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        if c.fetchone():
            st.warning(f"This movie is already in your favorites.")
        else:
            query = "INSERT INTO favorites (user_id, movie_id, date_added) VALUES (%s, %s, %s)"
            values = (user_id, movie_id, datetime.datetime.now())
            c.execute(query, values)
            conn.commit()
            st.success("Added to favorites!")

    # Function to delete ratings when removing favorites
    def delete_rating(user_id, movie_id):
        query = "DELETE FROM ratings WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        conn.commit()

    # Function to remove favorites
    def remove_favorite(user_id, movie_id):
        # Remove associated rating
        delete_rating(user_id, movie_id)
        # Remove favorite
        query = "DELETE FROM favorites WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        conn.commit()
        st.success("Removed from favorites!")
        st.session_state['favorites_updated'] = True

    # Function to save or update movie ratings
    def save_rating(user_id, movie_id, rating):
        query = "SELECT rating_id FROM ratings WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        result = c.fetchone()

        if result:
            # If it exists, update the rating
            query = "UPDATE ratings SET rating = %s, date = %s WHERE user_id = %s AND movie_id = %s"
            values = (rating, datetime.datetime.now(), user_id, movie_id)
        else:
            # If it doesn't exist, insert a new rating
            query = "INSERT INTO ratings (user_id, movie_id, rating, date) VALUES (%s, %s, %s, %s)"
            values = (user_id, movie_id, rating, datetime.datetime.now())

        c.execute(query, values)
        conn.commit()

    # Function to get the previous rating (if exists)
    def get_rating(user_id, movie_id):
        query = "SELECT rating FROM ratings WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        result = c.fetchone()
        if result:
            return result[0]  # Return the existing rating
        else:
            return None  # If no previous rating, return None

    # Show the favorite movies history
    def show_favorites(user_id):
        st.subheader(f"Your Favorite Movies")
        query = "SELECT movie_id FROM favorites WHERE user_id = %s"
        c.execute(query, (user_id,))
        favorites = c.fetchall()

        if favorites:
            # Group favorites in rows of 3 columns
            for i in range(0, len(favorites), 3):
                cols_favorites = st.columns(3)
                
                for col, fav in zip(cols_favorites, favorites[i:i+3]):
                    movie = df.loc[df.index == fav[0]].iloc[0]
                    short_title = movie['title'] if len(movie['title']) <= 20 else movie['title'][:20] + '...'
                    with col:
                        st.image(movie['poster'], width=150)
                        st.write(f"**{short_title}** ({movie['year']})")
                        st.write(f"Duration: {movie['duration']} min")

                        # Show rating slider only in favorites
                        previous_rating = get_rating(user_id, fav[0])
                        if previous_rating is None:
                            rating = st.slider(f"Rate", 1, 10, step=1, key=f"rate_fav_{fav[0]}")
                            if st.button(f"Submit Rating", key=f"submit_rating_fav_{fav[0]}"):
                                save_rating(user_id, fav[0], rating)
                        else:
                            st.write(f"Your rating for this movie: {previous_rating}")
                            rating = st.slider(f"Update rating", 1, 10, step=1, value=previous_rating, key=f"update_rating_fav_{fav[0]}")
                            if rating != previous_rating:
                                save_rating(user_id, fav[0], rating)

                        # Button to remove from favorites and delete rating
                        if st.button(f"❌ Remove favorite", key=f"remove_fav_{fav[0]}"):
                            remove_favorite(user_id, fav[0])

                # Add a continuous line only if it's not the last group
                if i + 3 < len(favorites):
                    st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.write("No favorites found.")

    # Load the movie dataset (adjust the path to your dataset if necessary)
    df = pd.read_csv('data/imdb_clean.csv')

    df['movie_id'] = df.index

    # Dictionary of emotions with emojis
    emotions_dict = {
        "Happy": "😊",
        "Down": "😢",
        "Excited": "🤩",
        "Relaxed": "😌",
        "Sweet": "❤️",
        "Scared": "😱",
        "Inspired": "🌟"
    }

    st.subheader("How are you feeling today?")
    selected_emotion = None

    # Display emotions using Streamlit buttons
    cols = st.columns(len(emotions_dict))

    for index, (emotion, emoji) in enumerate(emotions_dict.items()):
        with cols[index]:
            # Use st.button for interactive functionality
            if st.button(f"{emoji}\n{emotion}", key=f"emotion_{index}", use_container_width=True):
                selected_emotion = emotion

    # Save the selected emotion in st.session_state so it doesn't get lost
    if selected_emotion:
        st.session_state['selected_emotion'] = selected_emotion
        st.session_state['shown_movies'] = set()  # Reset shown movies when the emotion changes

    # If there's already a selected emotion in session_state, use it
    if 'selected_emotion' in st.session_state:
        selected_emotion = st.session_state['selected_emotion']

    # Display the selected emotion and recommendations ONLY if there's a selected emotion
    if selected_emotion:
        st.write(f"You selected: {emotions_dict[selected_emotion]} {selected_emotion}")

        # Filter movies based on the selected emotion
        filtered_movies = df[df['emotions'].apply(lambda x: selected_emotion in x)]

        # Add predicted ratings for each filtered movie
        filtered_movies['predicted_rating'] = filtered_movies['movie_id'].apply(lambda x: predict_rating(st.session_state['user_id'], x))

        # Sort movies by predicted rating
        filtered_movies = filtered_movies.sort_values(by='predicted_rating', ascending=False)

        # Limit the number of movies to display (between 6 and 12, with a default value of 6)
        num_movies_to_display = st.slider("Number of movies to display", min_value=6, max_value=12, value=6)

        # Initialize the list of shown movies if it doesn't exist in the session
        if 'shown_movies' not in st.session_state or not st.session_state['shown_movies']:
            # Randomly select the first movies
            initial_movies = filtered_movies.sample(n=num_movies_to_display).index.tolist()
            st.session_state['shown_movies'] = initial_movies
        else:
            # If the user increases the number of movies to display, add new movies
            if len(st.session_state['shown_movies']) < num_movies_to_display:
                # Get additional movies without repeating those already shown
                new_movies = filtered_movies[~filtered_movies.index.isin(st.session_state['shown_movies'])].sample(n=num_movies_to_display - len(st.session_state['shown_movies'])).index.tolist()
                st.session_state['shown_movies'].extend(new_movies)

        # Get the shown movies based on the stored indices
        shown_movies = filtered_movies.loc[st.session_state['shown_movies']]

        # Display the movies in a grid format (3 columns)
        for i in range(0, len(shown_movies), 3):
            cols_movies = st.columns(3)

            # Iterate over each group of 3 movies
            for col, (index, movie) in zip(cols_movies, shown_movies.iloc[i:i+3].iterrows()):
                with col:
                    short_title = movie['title'] if len(movie['title']) <= 20 else movie['title'][:20] + '...'

                    st.image(movie['poster'], width=150)
                    st.write(f"**{short_title}** ({movie['year']})")
                    st.write(f"Duration: {movie['duration']} min")
                    st.write(f"Rating: {movie['rating']}")

                    is_favorite_pred = predict_favorite([movie['duration'], movie['rating']])

                    # Register "shown" only if the movie hasn't been shown in this session
                    if not check_session_interaction(index):
                        save_interaction(st.session_state['user_id'], index, selected_emotion, "shown")
                        register_session_interaction(index)

                    # Expand description without the "Show more details" button
                    with st.expander("Description", expanded=False):
                        st.write(f"{movie['description']}")

                    # "Watch" button
                    if st.button(f"🎬 Watch", key=f"watch_{index}"):
                        update_interaction(st.session_state['user_id'], index, "view")

                    # Button to add to favorites
                    if st.button(f"❤️ Add to favorites", key=f"fav_{index}"):
                        save_favorite(st.session_state['user_id'], index)

            st.markdown("<hr>", unsafe_allow_html=True)

        st.write("")

    # Show the favorites history
    show_favorites(st.session_state['user_id'])