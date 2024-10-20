import mysql.connector
import streamlit as st
import pandas as pd
import datetime
import random

# Conectar a la base de datos MySQL
conn = mysql.connector.connect(
    host="localhost",  
    user="root",  
    password="123456",  
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
        st.rerun()

# Función para cerrar sesión
def cerrar_sesion():
    st.session_state.clear()  # Limpiar toda la sesión
    st.success("You have successfully logged out.")
    st.rerun()

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

    # Guardar interacciones en la base de datos usando el índice del DataFrame como movie_id
    def guardar_interaccion(user_id, movie_id, emotion, interaction_type):
        query = "INSERT INTO interactions (user_id, movie_id, emotion, interaction_type, date) VALUES (%s, %s, %s, %s, %s)"
        values = (user_id, movie_id, emotion, interaction_type, datetime.datetime.now())
        c.execute(query, values)
        conn.commit()

    # Verificar si la película ya ha sido mostrada en la sesión actual
    def verificar_interaccion_sesion(movie_id):
        if 'peliculas_mostradas' not in st.session_state:
            st.session_state['peliculas_mostradas'] = set()  # Usamos un conjunto para evitar duplicados en la sesión
        
        # Comprobar si la película ya fue mostrada en esta sesión
        return movie_id in st.session_state['peliculas_mostradas']
    
    # Registrar la película como mostrada en la sesión actual
    def registrar_interaccion_sesion(movie_id):        
        st.session_state['peliculas_mostradas'].add(movie_id)

    # Función para actualizar una interacción existente en la base de datos
    def actualizar_interaccion(user_id, movie_id, interaction_type):
        query = """
        UPDATE interactions 
        SET interaction_type = %s, date = %s 
        WHERE user_id = %s AND movie_id = %s AND interaction_type = 'shown'
        """
        values = (interaction_type, datetime.datetime.now(), user_id, movie_id)
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

    # Función para eliminar calificaciones al eliminar favoritos
    def eliminar_calificacion(user_id, movie_id):
        query = "DELETE FROM ratings WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        conn.commit()

    # Función para eliminar favoritos
    def eliminar_favorito(user_id, movie_id):
        # Eliminar calificación asociada
        eliminar_calificacion(user_id, movie_id)
        # Eliminar favorito
        query = "DELETE FROM favorites WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        conn.commit()
        st.success("Removed from favorites!")
        st.session_state['favoritos_actualizados'] = True

    # Función para guardar o actualizar calificaciones de las películas
    def guardar_calificacion(user_id, movie_id, rating):
        query = "SELECT rating_id FROM ratings WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        result = c.fetchone()

        if result:
            # Si ya existe, actualizamos la calificación
            query = "UPDATE ratings SET rating = %s, date = %s WHERE user_id = %s AND movie_id = %s"
            values = (rating, datetime.datetime.now(), user_id, movie_id)
        else:
            # Si no existe, insertamos una nueva calificación
            query = "INSERT INTO ratings (user_id, movie_id, rating, date) VALUES (%s, %s, %s, %s)"
            values = (user_id, movie_id, rating, datetime.datetime.now())

        c.execute(query, values)
        conn.commit()

    # Función para obtener la calificación previa (si existe)
    def obtener_calificacion(user_id, movie_id):
        query = "SELECT rating FROM ratings WHERE user_id = %s AND movie_id = %s"
        c.execute(query, (user_id, movie_id))
        result = c.fetchone()
        if result:
            return result[0]  # Devolver la calificación existente
        else:
            return None  # Si no hay calificación previa, devolver None

    # Mostrar el historial de favoritos
    def mostrar_favoritos(user_id):
        st.subheader(f"Your Favorite Movies")
        query = "SELECT movie_id FROM favorites WHERE user_id = %s"
        c.execute(query, (user_id,))
        favoritos = c.fetchall()

        if favoritos:
            # Agrupar favoritos en filas de 3 columnas
            for i in range(0, len(favoritos), 3):
                cols_favoritos = st.columns(3)
                
                for col, fav in zip(cols_favoritos, favoritos[i:i+3]):
                    pelicula = df.loc[df.index == fav[0]].iloc[0]
                    titulo_corto = pelicula['title'] if len(pelicula['title']) <= 20 else pelicula['title'][:20] + '...'
                    with col:
                        st.image(pelicula['poster'], width=150)
                        st.write(f"**{titulo_corto}** ({pelicula['year']})")
                        st.write(f"Duration: {pelicula['duration']} min")

                        # Mostrar el slider de calificación solo en favoritos
                        calificacion_previa = obtener_calificacion(user_id, fav[0])
                        if calificacion_previa is None:
                            rating = st.slider(f"Rate", 1, 10, step=1, key=f"rate_fav_{fav[0]}")
                            if st.button(f"Submit Rating", key=f"submit_rating_fav_{fav[0]}"):
                                guardar_calificacion(user_id, fav[0], rating)
                        else:
                            st.write(f"Your rating for this movie: {calificacion_previa}")
                            rating = st.slider(f"Update rating", 1, 10, step=1, value=calificacion_previa, key=f"update_rating_fav_{fav[0]}")
                            if rating != calificacion_previa:
                                guardar_calificacion(user_id, fav[0], rating)

                        # Botón para eliminar de favoritos y eliminar la calificación
                        if st.button(f"❌ Remove favorite", key=f"remove_fav_{fav[0]}"):
                            eliminar_favorito(user_id, fav[0])

                # Añadir una línea continua solo si no es el último grupo
                if i + 3 < len(favoritos):
                    st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.write("No favorites found.")

    # Cargar el dataset de películas (ajusta la ruta a tu dataset si es necesario)
    df = pd.read_csv('imdb_clean.csv')

    # Diccionario de emociones con emoticonos
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

    # Mostrar emociones usando botones de Streamlit
    cols = st.columns(len(emotions_dict))

    for index, (emotion, emoji) in enumerate(emotions_dict.items()):
        with cols[index]:
            # Usamos st.button para funcionalidad interactiva
            if st.button(f"{emoji}\n{emotion}", key=f"emotion_{index}", use_container_width=True):
                selected_emotion = emotion

    # Guardar la emoción seleccionada en st.session_state para que no se pierda
    if selected_emotion:
        st.session_state['selected_emotion'] = selected_emotion
        st.session_state['peliculas_mostradas'] = []  # Reiniciar las películas mostradas al cambiar de emoción

    # Si ya hay una emoción seleccionada en session_state, usarla
    if 'selected_emotion' in st.session_state:
        selected_emotion = st.session_state['selected_emotion']

    # Mostrar la emoción seleccionada y las recomendaciones SOLO si hay una emoción seleccionada
    if selected_emotion:
        st.write(f"You selected: {emotions_dict[selected_emotion]} {selected_emotion}")

        # Filtrar las películas según la emoción seleccionada
        peliculas_filtradas = df[df['emotions'].apply(lambda x: selected_emotion in x)]

        # Limitar el número de películas a mostrar (entre 6 y 12, con valor por defecto de 6)
        num_peliculas_a_mostrar = st.slider("Number of movies to display", min_value=6, max_value=12, value=6)

        # Inicializar la lista de películas mostradas si no existe en la sesión
        if 'peliculas_mostradas' not in st.session_state or not st.session_state['peliculas_mostradas']:
            # Seleccionamos aleatoriamente las primeras películas
            peliculas_iniciales = peliculas_filtradas.sample(n=num_peliculas_a_mostrar).index.tolist()
            st.session_state['peliculas_mostradas'] = peliculas_iniciales
        else:
            # Si el usuario aumenta el número de películas a mostrar, agregamos nuevas películas
            if len(st.session_state['peliculas_mostradas']) < num_peliculas_a_mostrar:
                # Obtener películas adicionales sin repetir las ya mostradas
                nuevas_peliculas = peliculas_filtradas[~peliculas_filtradas.index.isin(st.session_state['peliculas_mostradas'])].sample(n=num_peliculas_a_mostrar - len(st.session_state['peliculas_mostradas'])).index.tolist()
                st.session_state['peliculas_mostradas'].extend(nuevas_peliculas)

        # Obtener las películas mostradas basadas en los índices almacenados
        peliculas_mostradas = peliculas_filtradas.loc[st.session_state['peliculas_mostradas']]

        # Mostrar las películas en formato grid (en 3 columnas)
        for i in range(0, len(peliculas_mostradas), 3):
            cols_movies = st.columns(3)

            # Iterar sobre cada grupo de 3 películas
            for col, (index, pelicula) in zip(cols_movies, peliculas_mostradas.iloc[i:i+3].iterrows()):
                with col:
                    titulo_corto = pelicula['title'] if len(pelicula['title']) <= 20 else pelicula['title'][:20] + '...'

                    st.image(pelicula['poster'], width=150)
                    st.write(f"**{titulo_corto}** ({pelicula['year']})")
                    st.write(f"Duration: {pelicula['duration']} min")
                    st.write(f"Rating: {pelicula['rating']}")

                    # Registrar "shown" solo si la película no ha sido mostrada en esta sesión
                    if not verificar_interaccion_sesion(index):
                        guardar_interaccion(st.session_state['user_id'], index, selected_emotion, "shown")
                        registrar_interaccion_sesion(index)

                    # Expandir descripción sin el botón de "Show more details"
                    with st.expander("Description", expanded=False):
                        st.write(f"{pelicula['description']}")

                    # Botón "Ver Película"
                    if st.button(f"🎬 Watch", key=f"watch_{index}"):
                        actualizar_interaccion(st.session_state['user_id'], index, "view")

                    # Botón para añadir a favoritos
                    if st.button(f"❤️ Add to favorites", key=f"fav_{index}"):
                        guardar_favorito(st.session_state['user_id'], index)

            st.markdown("<hr>", unsafe_allow_html=True)

        st.write("")

    # Mostrar el historial de favoritos
    mostrar_favoritos(st.session_state['user_id'])