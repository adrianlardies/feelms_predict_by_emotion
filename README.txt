# 🎬 Feelms - Predict by Emotion

Welcome to Feelms, a movie recommendation app that suggests films based on your emotions! This app uses collaborative filtering and machine learning models to predict your favorite movies and ratings, all while interacting with a MySQL database hosted on AWS.

## Features

- **Emotion-based Recommendations**: Select how you're feeling, and Feelms will suggest movies tailored to your emotions (Happy, Excited, Relaxed, etc.).
- **User Authentication**: Create a new user or log in to your account with a secure system. 
- **Movie Ratings & Favorites**: Rate your favorite movies and save them for easy access in your personal favorites list.
- **Machine Learning Models**: 
  - **SVD (Collaborative Filtering)**: Predicts personalized movie ratings.
  - **Random Forest Classifier**: Predicts whether a movie will become a favorite based on features like duration and ratings.
- **Streamlit UI**: Simple and intuitive web interface built with [Streamlit](https://streamlit.io/), allowing seamless interaction with the recommendation system.
