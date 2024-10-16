import mysql.connector
import streamlit as st
import pandas as pd
import datetime

# Conectar a la base de datos MySQL
conn = mysql.connector.connect(
    host="localhost",  # Cambia esto si estás usando un servidor MySQL remoto
    user="root",  # Cambia esto al usuario de tu MySQL
    password="123456",  # Cambia esto a tu contraseña de MySQL
    database="movie_recommendations"
)
c = conn.cursor()

# Función para verificar si el usuario existe o crear uno nuevo
def obtener_o_crear_usuario(username, password):
    query = "SELECT user_id FROM users WHERE username = %s"
    c.execute(query, (username,))
    result = c.fetchone()

    if not result:
        # Si el usuario no existe, lo creamos con una contraseña
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        c.execute(query, (username, password))
        conn.commit()
        st.success(f"User {username} has been created.")
        return c.lastrowid  # Devolver el ID del nuevo usuario (user_id)
    else:
        # El usuario existe, validar contraseña
        query = "SELECT user_id FROM users WHERE username = %s AND password = %s"
        c.execute(query, (username, password))
        result = c.fetchone()
        if result:
            st.success(f"Welcome back, {username}!")
            return result[0]  # Devolver el ID del usuario existente (user_id)
        else:
            st.error("Incorrect password. Please try again.")
            return None

# Función para insertar interacciones
def guardar_interaccion(user_id, movie_id, emotion):
    query = "INSERT INTO interactions (user_id, movie_id, emotion, date) VALUES (%s, %s, %s, %s)"
    values = (user_id, movie_id, emotion, datetime.datetime.now())
    c.execute(query, values)
    conn.commit()

# Función para guardar favoritos
def guardar_favorito(user_id, movie_id):
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

# Función para guardar calificaciones de las películas
def guardar_calificacion(user_id, movie_id, rating):
    query = "INSERT INTO ratings (user_id, movie_id, rating, date) VALUES (%s, %s, %s, %s)"
    values = (user_id, movie_id, rating, datetime.datetime.now())
    c.execute(query, values)
    conn.commit()

# Mostrar el historial de favoritos
def mostrar_favoritos(user_id):
    st.subheader(f"Your Favorite Movies")
    query = "SELECT movie_id FROM favorites WHERE user_id = %s"
    c.execute(query, (user_id,))
    favoritos = c.fetchall()

    if favoritos:
        for fav in favoritos:
            pelicula = df.loc[df.index == fav[0]].iloc[0]
            st.write(f"**{pelicula['title']}** ({pelicula['year']}) - {pelicula['duration']} min")
            st.image(pelicula['poster'], width=150)
    else:
        st.write("No favorites found.")

# Cargar el dataset de películas (ajusta la ruta a tu dataset si es necesario)
df = pd.read_csv('imdb_clean.csv')

# Streamlit interface
st.title("Movie Recommendation Based on Your Emotion")

# Sistema de autenticación
st.subheader("Login or Create an Account")

# Pedir el username
username = st.text_input("Username")

# Pedir la contraseña
password = st.text_input("Password", type="password")

# Botón para iniciar sesión o registrarse
if st.button("Login / Register"):
    if username and password:
        user_id = obtener_o_crear_usuario(username, password)

        if user_id:
            st.write(f"Welcome, {username}!")

            # Diccionario de emociones con emoticonos
            emotions_dict = {
                "Happy": "😊",
                "Sad": "😢",
                "Excited": "🤩",
                "Relaxed": "😌",
                "Romantic": "❤️",
                "Scared": "😱",
                "Inspired": "🌟",
                "Motivated": "💪"
            }

            st.subheader("How are you feeling today?")
            selected_emotion = None

            # Crear una barra de búsqueda
            search_query = st.text_input("Search for a movie title:")

            # Seleccionar la emoción
            cols = st.columns(len(emotions_dict))

            for index, (emotion, emoji) in enumerate(emotions_dict.items()):
                with cols[index]:
                    if st.button(f"{emoji} {emotion}"):
                        selected_emotion = emotion

            # Mostrar la emoción seleccionada y las recomendaciones
            if selected_emotion:
                st.write(f"You selected: {emotions_dict[selected_emotion]} {selected_emotion}")
                
                # Filtrar las películas según la emoción seleccionada y la búsqueda
                peliculas_filtradas = df[df['emotions'].apply(lambda x: selected_emotion in x)]
                
                if search_query:
                    peliculas_filtradas = peliculas_filtradas[peliculas_filtradas['title'].str.contains(search_query, case=False)]
                
                st.write("We recommend these movies for you:")

                # Limitar el número de películas a mostrar
                num_peliculas_a_mostrar = st.slider("Number of movies to display", min_value=1, max_value=20, value=5)
                peliculas_mostradas = peliculas_filtradas.head(num_peliculas_a_mostrar)

                # Mostrar las películas en formato grid (en 3 columnas)
                cols_movies = st.columns(3)
                for i, (index, pelicula) in enumerate(peliculas_mostradas.iterrows()):
                    with cols_movies[i % 3]:
                        st.image(pelicula['poster'], width=150)
                        st.write(f"**{pelicula['title']}** ({pelicula['year']})")
                        st.write(f"Duration: {pelicula['duration']} min")
                        st.write(f"Rating: {pelicula['rating']}")
                        st.write("---")
                        
                        # Botón de añadir a favoritos
                        if st.button(f"❤️ Add {pelicula['title']} to favorites", key=f"fav_{index}"):
                            guardar_favorito(user_id, index)
                        
                        # Guardar la interacción en la base de datos
                        guardar_interaccion(user_id, index, selected_emotion)

                        # Calificación del usuario
                        rating = st.slider(f"Rate {pelicula['title']}", 1, 5, step=1, key=f"rate_{index}")
                        if rating:
                            guardar_calificacion(user_id, index, rating)
                
                # Botón para mostrar más películas (cargar más)
                if len(peliculas_filtradas) > num_peliculas_a_mostrar:
                    if st.button("Show more movies"):
                        num_peliculas_a_mostrar += 5
                        peliculas_mostradas = peliculas_filtradas.head(num_peliculas_a_mostrar)

            # Mostrar el historial de favoritos
            mostrar_favoritos(user_id)