CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    year VARCHAR(10),
    duration VARCHAR(20),
    rating VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    genre TEXT
);

CREATE TABLE IF NOT EXISTS actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS directors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS movie_genre(
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS movie_actor(
    movie_id INT,
    actor_id INT,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES actors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS movie_director(
    movie_id INT,
    director_id INT,
    PRIMARY KEY (movie_id, director_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (director_id) REFERENCES directors(id) ON DELETE CASCADE
);

