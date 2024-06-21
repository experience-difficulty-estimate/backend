import sqlite3


def create_database():
    conn = sqlite3.connect("experiences.db")
    c = conn.cursor()

    # experiences 테이블 생성
    c.execute(
        """CREATE TABLE IF NOT EXISTS experiences
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT NOT NULL,
                  embedding BLOB,
                  difficulty_scores TEXT)"""
    )

    conn.commit()
    conn.close()

    print("Database 'experiences.db' created successfully.")


if __name__ == "__main__":
    create_database()
