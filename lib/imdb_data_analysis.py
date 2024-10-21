import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function: Distribution of genres
def plot_genre_distribution(df, genre_to_emotion):
    # Explode the 'genre' column to make each genre in the list its own row
    df_exploded_genres = df.explode('genre')
    df_exploded_genres['genre'] = df_exploded_genres['genre'].str.strip()

    # Filter only the genres that are in the defined genre_to_emotion mapping
    valid_genres = set(genre_to_emotion.keys())
    df_exploded_genres = df_exploded_genres[df_exploded_genres['genre'].isin(valid_genres)]

    genre_counts = df_exploded_genres['genre'].value_counts()

    # Print extracted data
    print("Top 5 most frequent genres:")
    print(genre_counts.head())

    # Plot the distribution of genres
    plt.figure(figsize=(10, 6))
    genre_counts.plot(kind='bar')
    plt.title("Distribution of Movie Genres")
    plt.ylabel('Frequency')
    plt.xlabel('Genre')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Function: Distribution of movie durations
def plot_duration_distribution(df):
    # Filter movies with a maximum duration of 300 minutes
    df_filtered = df[df['duration'] <= 300]
    
    # Create the bin labels
    bins = range(0, 301, 15)
    bin_labels = [f"{i}-{i+14}" for i in bins[:-1]]  

    # Create a new column with the duration split into bins
    df_filtered['duration_bins'] = pd.cut(df_filtered['duration'], bins=bins, labels=bin_labels, right=False)

    # Count how many movies fall into each duration range
    duration_counts = df_filtered['duration_bins'].value_counts()

    # Display the top 5 most frequent duration ranges
    print("Top 5 duration ranges (in minutes):")
    print(duration_counts.sort_values(ascending=False).head())

    # Plot the distribution of durations in ascending order
    plt.figure(figsize=(10, 6))
    duration_counts.sort_index().plot(kind='bar')  # Sorting by index for plotting from low to high duration
    plt.title("Distribution of Movie Durations")
    plt.ylabel('Frequency')
    plt.xlabel('Duration (minutes)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Function: Distribution of release years
def plot_year_distribution(df):
    bins = list(range(df['year'].min(), 2026, 5))
    bin_labels = [f"{i}-{i+4}" for i in bins[:-1]] + ["2020-2025"]

    df['year_bins'] = pd.cut(df['year'], bins=bins + [2026], labels=bin_labels, right=False)

    year_counts = df['year_bins'].value_counts().sort_index()

    # Print extracted data
    print("Top 5 release year ranges:")
    print(year_counts.sort_values(ascending=False).head())

    # Plot the distribution of release years
    plt.figure(figsize=(10, 6))
    year_counts.plot(kind='bar')
    plt.title("Distribution of Movie Release Years")
    plt.ylabel('Frequency')
    plt.xlabel('Release Year Range')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Function: Distribution of movie ratings
def plot_rating_distribution(df):
    # Print statistics of ratings
    print(f"Rating stats: \nMin: {df['rating'].min()}, Max: {df['rating'].max()}, Mean: {df['rating'].mean():.2f}")

    # Plot the distribution of ratings
    plt.figure(figsize=(10, 6))
    plt.hist(df['rating'], bins=range(0, 11), edgecolor='white', align='left')
    plt.title("Distribution of Movie Ratings")
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.xticks(range(0, 11))
    plt.tight_layout()
    plt.show()

# Function: Distribution of emotions
def plot_emotion_distribution(df):
    df_exploded_emotions = df.explode('emotions')
    emotion_counts = df_exploded_emotions['emotions'].value_counts()

    # Print extracted data
    print("Top 5 emotions:")
    print(emotion_counts.head())

    # Plot the distribution of emotions
    plt.figure(figsize=(10, 6))
    emotion_counts.plot(kind='bar')
    plt.title("Distribution of Emotions")
    plt.xlabel("Emotions")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

# Function: Crosstab of genres and emotions
def plot_genre_emotion_crosstab(df):
    df_exploded_genres = df.explode('genre').explode('emotions')
    genre_emotion_crosstab = pd.crosstab(df_exploded_genres['genre'], df_exploded_genres['emotions'])

    # Print the crosstab data
    print("Genre and Emotion Crosstab:")
    print(genre_emotion_crosstab)

    # Plot the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(genre_emotion_crosstab, cmap='Blues', annot=True, fmt='d')
    plt.title("Genres vs. Emotions")
    plt.show()

# Function: Ratings vs Emotions
def plot_ratings_vs_emotions(df):
    df_exploded_emotions = df.explode('emotions')

    # Print the distribution of ratings for each emotion
    print("Ratings distribution by emotion:")
    print(df_exploded_emotions.groupby('emotions')['rating'].describe())

    plt.figure(figsize=(12, 6))
    sns.boxplot(x='emotions', y='rating', data=df_exploded_emotions, palette="Set2")
    plt.title("Relationship between Ratings and Emotions")
    plt.show()

# Analysis of directors and actors
def analyze_directors_actors(df):
    director_counts = df['director'].value_counts()

    actors_list = df['cast'].explode()
    actor_counts = actors_list.value_counts()

    # Print top directors and actors
    print("Top 5 directors:")
    print(director_counts.head())
    print("\nTop 5 actors:")
    print(actor_counts.head())

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
    avg_rating = df.groupby('year')['rating'].mean()

    # Print average ratings over time
    print("Average ratings over the years:")
    print(avg_rating)

    avg_rating.plot(kind='line', figsize=(10, 5), marker='o', color='orange')
    plt.title('Average Movie Ratings Over Time')
    plt.ylabel('Average Rating')
    plt.xlabel('Year')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Count of movies by emotion over time
    emotion_years = df.explode('emotions').groupby(['year', 'emotions']).size().unstack().fillna(0)

    # Print emotion trends over the years
    print("Emotion trends over the years:")
    print(emotion_years)

    emotion_years.plot(kind='area', figsize=(10, 6), stacked=True, alpha=0.7)
    plt.title('Emotion Trends Over the Years')
    plt.ylabel('Number of Movies')
    plt.xlabel('Year')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return avg_rating, emotion_years

# Compare genres and durations
def compare_genres_durations(df):
    genre_duration = df.explode('genre').groupby('genre')['duration'].mean().sort_values(ascending=False)

    # Print average duration by genre
    print("Average duration by genre (Top 5):")
    print(genre_duration.head())

    plt.figure(figsize=(10, 5))
    genre_duration.plot(kind='bar', color='purple')
    plt.title('Average Movie Duration by Genre')
    plt.ylabel('Average Duration (minutes)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return genre_duration