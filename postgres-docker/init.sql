CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    year VARCHAR(10),
    duration VARCHAR(20),
    rating VARCHAR(10)
);