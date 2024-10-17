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

# Función para manejar el estado de sesión del usuario
def iniciar_sesion(username, password):
    user_id = obtener_o_crear_usuario(username, password)
    if user_id:
        st.session_state['user_id'] = user_id
        st.session_state['username'] = username
        st.session_state['logged_in'] = True

# Función para cerrar sesión
def cerrar_sesion():
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None

# Inicializar el estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None

# Si el usuario no está logueado, mostramos el formulario de login/registro
if not st.session_state['logged_in']:
    st.title("Movie Recommendation Based on Your Emotion")

    # Pedir el username
    username = st.text_input("Username")

    # Pedir la contraseña
    password = st.text_input("Password", type="password")

    # Botón para iniciar sesión o registrarse
    if st.button("Login / Register"):
        if username and password:
            iniciar_sesion(username, password)
else:
    st.write(f"Welcome, {st.session_state['username']}!")

    # Botón para cerrar sesión
    if st.button("Logout"):
        cerrar_sesion()

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

    # Seleccionar la emoción
    cols = st.columns(len(emotions_dict))

    for index, (emotion, emoji) in enumerate(emotions_dict.items()):
        with cols[index]:
            if st.button(f"{emoji} {emotion}"):
                selected_emotion = emotion

    # Guardar la emoción seleccionada en st.session_state para que no se pierda
    if selected_emotion:
        st.session_state['selected_emotion'] = selected_emotion

    # Si ya hay una emoción seleccionada en session_state, usarla
    if 'selected_emotion' in st.session_state:
        selected_emotion = st.session_state['selected_emotion']

    # Mostrar la emoción seleccionada y las recomendaciones
    if selected_emotion:
        st.write(f"You selected: {emotions_dict[selected_emotion]} {selected_emotion}")

        # Filtrar las películas según la emoción seleccionada
        peliculas_filtradas = df[df['emotions'].apply(lambda x: selected_emotion in x)]

        st.write("We recommend these movies for you:")

        # Limitar el número de películas a mostrar (entre 6 y 12, con valor por defecto de 6)
        num_peliculas_a_mostrar = st.slider("Number of movies to display", min_value=6, max_value=12, value=6)
        peliculas_mostradas = peliculas_filtradas.head(num_peliculas_a_mostrar)

        # Mostrar las películas en formato grid (en 3 columnas)
        for i in range(0, len(peliculas_mostradas), 3):
            cols_movies = st.columns(3)
            
            # Iterar sobre cada grupo de 3 películas
            for col, (index, pelicula) in zip(cols_movies, peliculas_mostradas.iloc[i:i+3].iterrows()):
                with col:
                    # Truncar el título si excede los 20 caracteres
                    titulo_corto = pelicula['title'] if len(pelicula['title']) <= 20 else pelicula['title'][:20] + '...'

                    st.image(pelicula['poster'], width=150)
                    st.write(f"**{titulo_corto}** ({pelicula['year']})")
                    st.write(f"Duration: {pelicula['duration']} min")
                    st.write(f"Rating: {pelicula['rating']}")
                    with st.expander("Description"):
                        st.write(f"{pelicula['description']}")
                    st.write("---")
                    
                    # Truncar también en el botón de favoritos e incluir el año de la película
                    if st.button(f"❤️ Add {titulo_corto} ({pelicula['year']}) to favorites", key=f"fav_{index}"):
                        guardar_favorito(st.session_state['user_id'], index)
                    
                    # Guardar la interacción en la base de datos
                    guardar_interaccion(st.session_state['user_id'], index, selected_emotion)

                    # Calificación del usuario, truncando también el título en el slider de calificación
                    rating = st.slider(f"Rate {titulo_corto}", 1, 10, step=1, key=f"rate_{index}")
                    if rating:
                        guardar_calificacion(st.session_state['user_id'], index, rating)
            
            # Añadir un espaciado extra después de cada fila de 3 películas
            st.write("")  # Línea vacía para crear espacio
            st.markdown("<hr>", unsafe_allow_html=True)  # Línea horizontal para separar las filas


        # Mostrar el historial de favoritos
        mostrar_favoritos(st.session_state['user_id'])