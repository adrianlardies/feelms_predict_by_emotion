import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function: Distribution of genres
def plot_genre_distribution(df):
    df_exploded_genres = df.explode('genre')
    genre_counts = df_exploded_genres['genre'].value_counts()
    genre_counts.plot(kind='bar', figsize=(10,6), title="Distribution of Movie Genres")
    plt.show()

# Function: Distribution of movie durations
def plot_duration_distribution(df):
    df['duration'].plot(kind='hist', bins=20, figsize=(10,6), title="Distribution of Movie Durations (in minutes)")
    plt.xlabel('Duration (minutes)')
    plt.show()

# Function: Distribution of release years
def plot_year_distribution(df):
    df['year'].plot(kind='hist', bins=15, figsize=(10,6), title="Distribution of Movie Release Years")
    plt.xlabel('Release Year')
    plt.show()

# Function: Distribution of ratings
def plot_rating_distribution(df):
    df['rating'].plot(kind='hist', bins=20, figsize=(10,6), title="Distribution of Movie Ratings")
    plt.xlabel('Rating')
    plt.show()

# Function: Distribution of emotions
def plot_emotion_distribution(df):
    df_exploded_emotions = df.explode('emotions')
    emotion_counts = df_exploded_emotions['emotions'].value_counts()
    emotion_counts.plot(kind='bar', figsize=(10,6), title="Distribution of Emotions Associated with Movies")
    plt.show()

# Function: Crosstab of genres and emotions
def plot_genre_emotion_crosstab(df):
    df_exploded_genres = df.explode('genre').explode('emotions')
    genre_emotion_crosstab = pd.crosstab(df_exploded_genres['genre'], df_exploded_genres['emotions'])
    plt.figure(figsize=(12,8))
    sns.heatmap(genre_emotion_crosstab, cmap='Blues', annot=True)
    plt.title("Genres vs. Emotions Heatmap")
    plt.show()

# Function: Ratings vs Emotions
def plot_ratings_vs_emotions(df):
    df_exploded_emotions = df.explode('emotions')
    sns.boxplot(x='emotions', y='rating', data=df_exploded_emotions, palette="Set2")
    plt.title("Relationship between Ratings and Emotions")
    plt.show()

# Analysis of directors and actors
def analyze_directors_actors(df):
    # Count the frequency of each director
    director_counts = df['director'].value_counts()

    # Count the frequency of each actor
    actors_list = df['cast'].explode()  # Explode the list of actors into individual rows
    actor_counts = actors_list.value_counts()

    # Plot the top 10 directors
    plt.figure(figsize=(10, 5))
    director_counts.head(10).plot(kind='bar', color='skyblue')
    plt.title('Top 10 Most Frequent Directors')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Plot the top 10 actors
    plt.figure(figsize=(10, 5))
    actor_counts.head(10).plot(kind='bar', color='lightgreen')
    plt.title('Top 10 Most Frequent Actors')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return director_counts, actor_counts

# Trends over time (years)
def analyze_time_trends(df):
    # Average rating over time
    df.groupby('year')['rating'].mean().plot(kind='line', figsize=(10, 5), marker='o', color='orange')
    plt.title('Average Movie Ratings Over Time')
    plt.ylabel('Average Rating')
    plt.xlabel('Year')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Count of movies by emotion over time
    emotion_years = df.explode('emotions').groupby(['year', 'emotions']).size().unstack().fillna(0)
    emotion_years.plot(kind='line', figsize=(10, 5), marker='o')
    plt.title('Emotion Trends Over the Years')
    plt.ylabel('Number of Movies')
    plt.xlabel('Year')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return df.groupby('year')['rating'].mean(), emotion_years

# Compare genres and durations
def compare_genres_durations(df):
    # Explode genres and calculate average duration for each genre
    genre_duration = df.explode('genre').groupby('genre')['duration'].mean().sort_values(ascending=False)

    # Plot the average duration by genre
    plt.figure(figsize=(10, 5))
    genre_duration.plot(kind='bar', color='purple')
    plt.title('Average Movie Duration by Genre')
    plt.ylabel('Average Duration (minutes)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return genre_duration

