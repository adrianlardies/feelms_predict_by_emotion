import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Function: Interaction type distribution
def interaction_type_distribution(df_interactions):
    interaction_counts = df_interactions['interaction_type'].value_counts()
    print("Interaction type distribution:\n", interaction_counts)
    
    plt.figure(figsize=(10, 6))  # Set a bigger size for the plot
    interaction_counts.plot(kind='bar')
    plt.title('Distribution of Interaction Types')
    plt.ylabel('Frequency')
    plt.xlabel('Interaction Type')
    plt.xticks(rotation=45, ha='right')  # Rotate for better readability
    plt.tight_layout()
    plt.show()

# Function: Emotion distribution in interactions
def emotion_distribution_in_interactions(df_interactions):
    emotion_counts = df_interactions['emotion'].value_counts()
    print("Emotion distribution in interactions:\n", emotion_counts)
    
    plt.figure(figsize=(10, 6))
    emotion_counts.plot(kind='bar')
    plt.title('Emotion Distribution in Interactions')
    plt.ylabel('Frequency')
    plt.xlabel('Emotion')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Function: Interactions over time with monthly print
def interaction_over_time(df_interactions):
    df_interactions['date'] = pd.to_datetime(df_interactions['date'])
    
    # Group by month and count the number of interactions
    interactions_per_month = df_interactions.groupby(df_interactions['date'].dt.to_period('M')).size()
    
    # Print the monthly interactions
    print("Number of interactions per month:\n", interactions_per_month)
    
    # Plot the interactions over time
    plt.figure(figsize=(10, 6))
    interactions_per_month.plot(kind='line', marker='o')
    plt.title('Interactions Over Time')
    plt.ylabel('Number of Interactions')
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

# Function: Favorites per user
def favorites_per_user(df_favorites):
    user_favorites = df_favorites['user_id'].value_counts()
    print("Favorites per user (Top 10):\n", user_favorites.head(10))
    
    # Plot the histogram with separated bars
    plt.figure(figsize=(10, 6))
    plt.hist(user_favorites, bins=range(0, 26), width=0.8, align='left')  # Reduce bar width to separate them
    plt.title('Distribution of Favorites per User')
    plt.xlabel('Number of Favorites')
    plt.ylabel('Frequency')
    plt.xticks(range(0, 26))  # Ensure x-axis has integer values
    plt.tight_layout()
    plt.show()

# Function: Favorite emotion distribution
def favorite_emotion_distribution(df_favorites, df_interactions):
    df_merged = pd.merge(df_favorites, df_interactions[['movie_id', 'emotion']], on='movie_id')
    emotion_counts = df_merged['emotion'].value_counts()
    print("Emotion distribution in favorite movies:\n", emotion_counts)
    
    plt.figure(figsize=(10, 6))
    emotion_counts.plot(kind='bar')
    plt.title('Emotion Distribution in Favorite Movies')
    plt.ylabel('Frequency')
    plt.xlabel('Emotion')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# Function: Rating distribution
def rating_distribution(df_ratings):
    print("Rating distribution:\n", df_ratings['rating'].value_counts())
    
    # Plot the histogram with separated bars
    plt.figure(figsize=(10, 6))
    plt.hist(df_ratings['rating'], bins=range(1, 12), width=0.8, align='left')  # Reduce bar width to separate them
    plt.title('Distribution of Movie Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.xticks(range(1, 11))  # Ensure x-axis shows integer values from 1 to 10
    plt.tight_layout()
    plt.show()

# Function: Ratings by emotion
def ratings_by_emotion(df_ratings, df_interactions):
    # Merge the ratings with the corresponding emotions
    df_merged = pd.merge(df_ratings, df_interactions[['movie_id', 'emotion']], on='movie_id')
    
    # Print statistical summary of ratings grouped by emotion
    emotion_stats = df_merged.groupby('emotion')['rating'].describe()
    print("Rating statistics by emotion:\n", emotion_stats)
    
    # Plot the boxplot of ratings by emotion
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='emotion', y='rating', data=df_merged, palette="Set2")
    plt.title('Ratings by Emotion')
    plt.tight_layout()
    plt.show()

# Function: Interactions per user type (active vs less active)
def interactions_per_user(df_interactions, active_users, less_active_users):
    df_active = df_interactions[df_interactions['user_id'].isin(active_users)]
    df_less_active = df_interactions[df_interactions['user_id'].isin(less_active_users)]

    active_interactions = df_active['user_id'].value_counts()
    less_active_interactions = df_less_active['user_id'].value_counts()

    # Print summary of interactions
    print("Active Users - Interaction Stats:")
    print(active_interactions.describe())  # Provides count, mean, std, min, 25%, 50%, 75%, max
    
    print("\nLess Active Users - Interaction Stats:")
    print(less_active_interactions.describe())  # Same statistics for less active users
    
    # Visualization
    plt.figure(figsize=(10, 6))
    plt.hist([active_interactions, less_active_interactions], label=['Active', 'Less Active'], bins=20, alpha=0.7)
    plt.title('Interactions per User: Active vs Less Active')
    plt.xlabel('Number of Interactions')
    plt.ylabel('Frequency')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

# Function: Analyze favorites from views
def analyze_favorites_from_views(df_interactions, df_favorites):
    # Filter interactions of type 'view'
    df_views = df_interactions[df_interactions['interaction_type'] == 'view']

    # Merge with favorites to see which 'view' interactions are also in favorites
    df_merged = pd.merge(df_views[['user_id', 'movie_id']], df_favorites, on=['user_id', 'movie_id'], how='left', indicator=True)

    # Count how many 'view' interactions were also marked as favorites
    views_with_favorites = df_merged[df_merged['_merge'] == 'both'].shape[0]
    total_views = df_views.shape[0]

    # Calculate the proportion of views that became favorites
    favorite_proportion = views_with_favorites / total_views if total_views > 0 else 0

    # Print the results
    print(f"Total 'view' interactions: {total_views}")
    print(f"Views marked as favorites: {views_with_favorites}")
    print(f"Proportion of views that became favorites: {favorite_proportion:.2%}")

    # Visualize the proportions using a pie chart
    plt.figure(figsize=(6, 6))
    plt.pie([views_with_favorites, total_views - views_with_favorites],
            labels=['Favorites', 'Non-favorites'], autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
    plt.title('Proportion of Views Marked as Favorites')
    plt.tight_layout()
    plt.show()

    return favorite_proportion

# Function: Violin plot of Ratings by Emotion with print of statistics
def violin_ratings_by_emotion(df_ratings, df_interactions):
    df_merged = pd.merge(df_ratings, df_interactions[['movie_id', 'emotion']], on='movie_id')

    # Print the statistical summary
    stats = df_merged.groupby('emotion')['rating'].describe()
    print("Rating Statistics by Emotion:\n", stats)

    # Violin plot
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='emotion', y='rating', data=df_merged, palette="Set2")
    plt.title('Violin Plot: Ratings by Emotion')
    plt.tight_layout()
    plt.show()

# Function: Most recommended movies (shown)
def most_recommended_movies(df_interactions, df_movies):
    # Filter interactions where the movie was 'shown'
    shown_interactions = df_interactions[df_interactions['interaction_type'] == 'shown']
    
    # Count how many times each movie_id has been shown
    most_shown = shown_interactions['movie_id'].value_counts().head(10)
    
    # Reset index for the count dataframe, keeping 'movie_id' instead of 'index'
    most_shown = most_shown.rename('count').reset_index().rename(columns={'index': 'movie_id'})
    
    # Merge the counts with the movie titles on 'movie_id'
    most_shown_movies = pd.merge(most_shown, df_movies[['title']], left_on='movie_id', right_index=True)
    
    # Print the result
    print("Top 10 Most Recommended Movies (shown):")
    print(most_shown_movies)
    
    # Plot the result
    plt.figure(figsize=(10, 6))
    sns.barplot(x='count', y='title', data=most_shown_movies, palette='Blues_d')
    plt.title('Top 10 Most Recommended Movies (Shown)')
    plt.xlabel('Number of Times Shown')
    plt.ylabel('Movie Title')
    plt.tight_layout()
    plt.show()

# Function: Favorite directors, years, and correlations
def analyze_directors_years(df_interactions, df_movies):
    # Merge interactions with movies data to get director and year information
    df_merged = pd.merge(df_interactions, df_movies[['title', 'director', 'year']], left_on='movie_id', right_index=True, how='inner')

    # Group by director and count the number of interactions for each director
    director_counts = df_merged['director'].value_counts().head(10)
    
    # Group by year and count the number of interactions for each year
    year_counts = df_merged['year'].value_counts().sort_index()

    # Print top 10 favorite directors
    print("Top 10 Favorite Directors (by number of interactions):")
    print(director_counts)

    # Print interactions per year
    print("\nInteractions per Year:")
    print(year_counts)
    
    # Plot favorite directors
    plt.figure(figsize=(10, 6))
    director_counts.plot(kind='bar', color='lightblue')
    plt.title('Top 10 Favorite Directors (by interactions)')
    plt.xlabel('Director')
    plt.ylabel('Number of Interactions')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # Plot interactions per year
    plt.figure(figsize=(10, 6))
    year_counts.plot(kind='line', marker='o', color='orange')
    plt.title('Interactions per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Interactions')
    plt.tight_layout()
    plt.show()