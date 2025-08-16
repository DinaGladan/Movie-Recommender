CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    year VARCHAR(10),
    duration VARCHAR(20),
    rating VARCHAR(10),
    content_rating VARCHAR(10),
    number_of_users_reviews VARCHAR(20),
    number_of_critic_reviews VARCHAR(20),
    nominations_and_awards VARCHAR(50)
);

ALTER TABLE movies
ADD COLUMN imdb_id VARCHAR(20),
ADD COLUMN tmdb_id VARCHAR(20),
ADD COLUMN countries VARCHAR(255),
ADD COLUMN studio VARCHAR(255),
ADD COLUMN rt_critic_rating VARCHAR(10),
ADD COLUMN rt_audience_rating VARCHAR(10),
ADD COLUMN tmdb_audience_rating VARCHAR(10),
ADD COLUMN user_rating VARCHAR(10),
ADD COLUMN adult BOOLEAN,
ADD COLUMN original_language VARCHAR(10),
ADD COLUMN popularity VARCHAR(20),
ADD COLUMN release_date VARCHAR(20),
ADD COLUMN vote_count_tmdb VARCHAR(20);


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

CREATE TABLE IF NOT EXISTS writers (
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

CREATE TABLE IF NOT EXISTS movie_writer(
    movie_id INT,
    writer_id INT,
    PRIMARY KEY (movie_id, writer_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (writer_id) REFERENCES writers(id) ON DELETE CASCADE
);

