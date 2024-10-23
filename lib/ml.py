import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
from sklearn.impute import SimpleImputer

# 1. Preprocess the data: Merge, scale, and normalize
def preprocess_data(df_interactions, df_ratings, df_favorites, df_movies):
    # Merge interactions with movie data
    df_merged = pd.merge(df_interactions, df_movies, left_on='movie_id', right_index=True, how='inner')
    
    # Merge with ratings
    df_merged = pd.merge(df_merged, df_ratings[['user_id', 'movie_id', 'rating']], on=['user_id', 'movie_id'], how='left')
    
    # Merge with favorites (add a column 'is_favorite' to indicate whether the movie was favorited)
    df_merged = pd.merge(df_merged, df_favorites[['user_id', 'movie_id']], on=['user_id', 'movie_id'], how='left', indicator=True)
    df_merged['is_favorite'] = df_merged['_merge'] == 'both'
    df_merged.drop(columns=['_merge'], inplace=True)

    # Check if 'duration' exists and apply scaling
    if 'duration' in df_merged.columns:
        scaler = StandardScaler()
        df_merged[['duration']] = scaler.fit_transform(df_merged[['duration']])
    else:
        print("Column 'duration' not found. Skipping scaling.")
    
    return df_merged

# 2. Train SVD collaborative filtering model with manual hyperparameter adjustment
def train_svd_model(df_user_movie):
    # Prepare the data for Surprise's SVD
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(df_user_movie[['user_id', 'movie_id', 'rating']].dropna(), reader)
    
    # Manually adjust hyperparameters for SVD
    svd_model = SVD(n_factors=100, lr_all=0.005, reg_bi=0.1, reg_bu=0.1)  # Customize hyperparameters
    # svd_model = SVD(n_factors=100, n_epochs=50)  # You can uncomment this to test n_epochs

    # Cross-validation to evaluate the model
    results = cross_validate(svd_model, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
    
    return svd_model, results

# 3. Train RandomForest for classification with custom hyperparameters
def train_random_forest(df_user_movie):
    df_user_movie = pd.get_dummies(df_user_movie, columns=['genre', 'emotions'])

    # Prepare the features (X) and target (y)
    X = df_user_movie[['duration', 'rating']].fillna(0)  # Add more features as needed
    y = df_user_movie['is_favorite']
    
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(max_depth=15, random_state=42)

    # Train the RandomForest classifier
    rf.fit(X_train, y_train)
    
    # Make predictions
    y_pred = rf.predict(X_test)
    
    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    return rf, accuracy, precision, recall, f1, X_test, y_test  # Return X_test, y_test for later use

# 4. Evaluate classification model (e.g., RandomForest) and return the evaluation metrics
def evaluate_classification_model(y_test, y_pred):
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    return accuracy, precision, recall, f1

# 5. Confusion matrix for classification
def evaluate_classification(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    return cm