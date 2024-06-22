import os
import sqlite3
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OLD_DATABASE_PATH = "experiences.db"
NEW_DATABASE_PATH = "new_experiences.db"


def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_new_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-large")
    return response.data[0].embedding


def migrate_database():
    # Connect to the old database
    old_conn = get_db_connection(OLD_DATABASE_PATH)
    old_cur = old_conn.cursor()

    # Create the new database
    new_conn = get_db_connection(NEW_DATABASE_PATH)
    new_conn.execute(
        """CREATE TABLE IF NOT EXISTS new_experiences
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         text TEXT NOT NULL,
                         embedding BLOB,
                         difficulty_scores TEXT,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )

    # Fetch all data from the old database
    old_cur.execute("SELECT text, difficulty_scores FROM experiences")
    old_experiences = old_cur.fetchall()

    # Migrate data to the new database
    for exp in old_experiences:
        text, difficulty_scores = exp["text"], exp["difficulty_scores"]
        new_embedding = get_new_embedding(text)
        new_conn.execute(
            "INSERT INTO new_experiences (text, embedding, difficulty_scores) VALUES (?, ?, ?)",
            (text, np.array(new_embedding).tobytes(), difficulty_scores),
        )

    # Commit changes and close connections
    new_conn.commit()
    old_conn.close()
    new_conn.close()

    # Replace the old database with the new one
    os.remove(OLD_DATABASE_PATH)
    os.rename(NEW_DATABASE_PATH, OLD_DATABASE_PATH)

    print("Database migration completed successfully.")


if __name__ == "__main__":
    migrate_database()
