CREATE DATABASE event_portal;
USE event_portal;

CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    date DATE,
    description TEXT
);

CREATE TABLE registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    name VARCHAR(100),
    email VARCHAR(100),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
