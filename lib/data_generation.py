import random
import pandas as pd
import datetime
import mysql.connector

# Step 1: Generate Users
def generate_users(num_users):
    users = []
    for user_id in range(1, num_users + 1):
        username = f"user_{user_id}"
        password = f"pass_{user_id}"
        users.append([user_id, username, password])
    return pd.DataFrame(users, columns=['user_id', 'username', 'password'])

# Function to classify users as active and less active
def classify_users(df_users):
    active_users = df_users.sample(frac=0.2).user_id.tolist()  # 20% active users
    less_active_users = df_users[~df_users['user_id'].isin(active_users)].user_id.tolist()  # 80% less active users
    return active_users, less_active_users

# Function to generate interactions based on active and less active users
def generate_interactions(num_interactions, df_movies, df_users, active_users, less_active_users, emotions):
    interactions = []
    interaction_history = {}

    # Proportion: 1 out of 6 interactions will be 'view', the rest 'shown'
    view_ratio = 1 / 6
    shown_ratio = 5 / 6

    for _ in range(num_interactions):
        # Select either an active or less active user
        if random.random() > 0.3:
            user_id = random.choice(active_users)
        else:
            user_id = random.choice(less_active_users)

        # Select a random emotion
        emotion = random.choice(emotions)

        # Filter movies based on the selected emotion
        filtered_movies = df_movies[df_movies['emotions'].apply(lambda x: emotion in x)]

        # Continue only if there are movies matching the selected emotion
        if not filtered_movies.empty:
            # Select a random movie
            movie_id = filtered_movies.sample(1).index[0]

            # Initialize interaction history for the user if it doesn't exist
            if user_id not in interaction_history:
                interaction_history[user_id] = {}

            # Initialize history for the movie if it doesn't exist
            if movie_id not in interaction_history[user_id]:
                interaction_history[user_id][movie_id] = []

            # Determine if the interaction is 'shown' or 'view'
            if len(interaction_history[user_id][movie_id]) == 0:
                if random.random() < shown_ratio:
                    interaction_type = 'shown'
                else:
                    interaction_type = 'view'
            else:
                continue  # Skip if interaction exists

            # Generate a random date within the last year
            date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))

            # Add interaction to the list
            interactions.append([user_id, movie_id, emotion, interaction_type, date])

            # Track interaction to avoid duplicates
            interaction_history[user_id][movie_id].append(interaction_type)

    return pd.DataFrame(interactions, columns=['user_id', 'movie_id', 'emotion', 'interaction_type', 'date'])

# Function to generate favorites based on interactions (only 'view')
def generate_favorites(df_interactions):
    favorites = []

    # Select only 'view' interactions
    viewed_interactions = df_interactions[df_interactions['interaction_type'] == 'view']

    # Select 30% of viewed interactions as favorites
    num_favorites = int(len(viewed_interactions) * 0.3)

    for _, selected_interaction in viewed_interactions.sample(num_favorites).iterrows():
        user_id = selected_interaction['user_id']
        movie_id = selected_interaction['movie_id']
        view_date = selected_interaction['date']

        # Ensure that the favorite date is after the viewing date
        days_after = random.randint(0, (datetime.datetime.now() - view_date).days)
        date_added = view_date + datetime.timedelta(days=days_after)

        favorites.append([user_id, movie_id, date_added])

    return pd.DataFrame(favorites, columns=['user_id', 'movie_id', 'date_added'])

# Function to generate ratings based on 50% of the favorites
def generate_ratings(df_favorites):
    ratings = []

    # Select 50% of the favorite movies to be rated
    num_ratings = int(len(df_favorites) * 0.5)

    for _, selected_favorite in df_favorites.sample(num_ratings).iterrows():
        user_id = selected_favorite['user_id']
        movie_id = selected_favorite['movie_id']
        favorite_date = selected_favorite['date_added']

        # Ensure the rating date is after or equal to the favorite date
        days_after = random.randint(0, (datetime.datetime.now() - favorite_date).days)
        date_rated = favorite_date + datetime.timedelta(days=days_after)

        # Assign a rating between 1 and 10, with a bias towards higher ratings
        rating = random.choices(range(1, 11), weights=[1, 1, 2, 2, 3, 3, 4, 4, 5, 5], k=1)[0]

        ratings.append([user_id, movie_id, rating, date_rated])

    return pd.DataFrame(ratings, columns=['user_id', 'movie_id', 'rating', 'date'])

# Function to insert data into MySQL
def insert_users(df_users, conn, cursor):
    for _, row in df_users.iterrows():
        query = """
        INSERT INTO users (user_id, username, password) 
        VALUES (%s, %s, %s)
        """
        values = (row['user_id'], row['username'], row['password'])
        cursor.execute(query, values)
    conn.commit()

def insert_interactions(df_interactions, conn, cursor):
    for _, row in df_interactions.iterrows():
        query = """
        INSERT INTO interactions (user_id, movie_id, emotion, interaction_type, date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (row['user_id'], row['movie_id'], row['emotion'], row['interaction_type'], row['date'])
        cursor.execute(query, values)
    conn.commit()

def insert_favorites(df_favorites, conn, cursor):
    for _, row in df_favorites.iterrows():
        query = """
        INSERT INTO favorites (user_id, movie_id, date_added) 
        VALUES (%s, %s, %s)
        """
        values = (row['user_id'], row['movie_id'], row['date_added'])
        cursor.execute(query, values)
    conn.commit()

def insert_ratings(df_ratings, conn, cursor):
    for _, row in df_ratings.iterrows():
        query = """
        INSERT INTO ratings (user_id, movie_id, rating, date) 
        VALUES (%s, %s, %s, %s)
        """
        values = (row['user_id'], row['movie_id'], row['rating'], row['date'])
        cursor.execute(query, values)
    conn.commit()

# Function to connect to MySQL
def connect_to_mysql():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="movie_recommendations"
    )
    return conn, conn.cursor()