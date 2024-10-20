# data_cleaning.py
import pandas as pd

# Function to clean the dataframe
def clean_movie_data(file_path):
    df = pd.read_csv(file_path)
    
    # Remove unnecessary columns
    df = df.drop(columns=['Metascore', 'Votes', 'Review Count', 'Review Title', 'Review', 'Certificate']) 

    # Drop rows with missing values
    df = df.dropna()

    # Rename columns
    df.rename(columns={
        'Poster': 'poster', 
        'Title': 'title', 
        'Year': 'year', 
        'Duration (min)': 'duration', 
        'Genre': 'genre', 
        'Rating': 'rating', 
        'Director': 'director', 
        'Cast': 'cast', 
        'Description': 'description'
    }, inplace=True)

    # Convert types
    df['year'] = df['year'].astype(int)
    df['duration'] = df['duration'].astype(int)

    # Clean genre and cast columns
    df['genre'] = df['genre'].apply(lambda x: x.split(','))
    df['cast'] = df['cast'].apply(lambda x: x.split(', '))

    # Strip whitespace from string columns
    df['title'] = df['title'].str.strip()
    df['description'] = df['description'].str.strip()
    df['director'] = df['director'].str.strip()

    # Clean up genre column
    df['genre'] = df['genre'].apply(lambda genres: [genre.strip() for genre in genres])

    return df

# Mapping function for genres to emotions
def map_genres_to_emotions(df, genre_to_emotion):
    def map_genres(genres):
        emotions = set()  # Use set to avoid duplicates
        for genre in genres:
            if genre.strip() in genre_to_emotion:
                emotions.update(genre_to_emotion[genre.strip()])  # Add corresponding emotions to the genre
        return list(emotions)

    df['emotions'] = df['genre'].apply(map_genres)
    return df

# Function to extract unique emotions
def extract_unique_emotions(df):
    return set([emotion for emotion_list in df['emotions'] for emotion in emotion_list])