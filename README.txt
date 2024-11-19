*SQLITE DATABASE CREATION*

1. Create a sqlite database using the name "notetaker.db"

2. Create tables using the following code in notetaker.db

CREATE TABLE users (
id INTEGER PRIMARY KEY,
hash TEXT,
username TEXT);

CREATE TABLE notes (
user_id INTEGER PRIMARY KEY,
textareas TEXT NOT NULL,
canvas TEXT NOT NULL, name TEXT);

*HANDWRITTEN TEXT RECOGNITION (HTR) CREATION*

1. Create folder named "model"

2. Run htr.py

