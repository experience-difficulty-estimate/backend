from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import sqlite3
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect("experiences.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS experiences
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT,
                  embedding BLOB,
                  difficulty_scores TEXT)"""
    )
    conn.commit()
    conn.close()


init_db()

INITIAL_PROMPT = """You are an AI assistant specialized in estimating the difficulty of various life experiences. You will receive descriptions of experiences and should respond with a difficulty assessment based on the following 10 metrics:

1. 육체적 힘듦 (Physical Difficulty)
2. 정신적 노력 (Mental Effort)
3. 시간 투자 (Time Investment)
4. 기술적 복잡성 (Technical Complexity)
5. 사회적 도전 (Social Challenge)
6. 재정적 부담 (Financial Burden)
7. 위험도 (Risk Level)
8. 지속성 요구 (Persistence Required)
9. 창의성 요구 (Creativity Needed)
10. 희소성 (Rarity)

For each experience, provide a score from 0 to 100 for each metric, where 0 is extremely easy/common and 100 is extremely difficult/rare.

Consider factors like duration, consistency, intensity, time commitment, complexity, social implications, financial costs, risks, persistence required, creativity needed, and rarity.

Respond with a JSON array of 10 numbers representing the scores for each metric in the order listed above. Your response should only contain this JSON array, no additional text."""


def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding


def get_difficulty_scores(experience):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": INITIAL_PROMPT},
            {"role": "user", "content": f"Estimate the difficulty of: {experience}"},
        ],
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)


def find_similar_experience(embedding, threshold=0.9):
    conn = sqlite3.connect("experiences.db")
    c = conn.cursor()
    c.execute("SELECT id, text, embedding, difficulty_scores FROM experiences")
    experiences = c.fetchall()
    conn.close()

    if not experiences:
        return None, 0

    similarities = []
    for exp in experiences:
        exp_embedding = np.frombuffer(exp[2], dtype=np.float32)
        similarity = cosine_similarity([embedding], [exp_embedding])[0][0]
        similarities.append((exp, similarity))

    most_similar = max(similarities, key=lambda x: x[1])
    if most_similar[1] > threshold:
        return most_similar[0], most_similar[1]
    return None, 0


def get_db_connection():
    try:
        conn = sqlite3.connect("experiences.db")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


@app.route("/api/estimate", methods=["POST"])
def estimate_difficulty():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    experience = data.get("experience")
    if not experience:
        return jsonify({"error": "No experience provided"}), 400

    try:
        embedding = get_embedding(experience)
        similar_exp, similarity = find_similar_experience(embedding)

        if similar_exp and similarity > 0.95:
            difficulty_scores = json.loads(similar_exp[3])
        else:
            difficulty_scores = get_difficulty_scores(experience)

        total_difficulty = sum(difficulty_scores) / len(difficulty_scores)
        level = int(total_difficulty / 10) + 1

        # 데이터베이스에 저장
        conn = sqlite3.connect("experiences.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO experiences (text, embedding, difficulty_scores) VALUES (?, ?, ?)",
            (experience, np.array(embedding).tobytes(), json.dumps(difficulty_scores)),
        )
        conn.commit()
        conn.close()

        return jsonify(
            {
                "experience": experience,
                "difficulty_scores": difficulty_scores,
                "total_difficulty": total_difficulty,
                "level": level,
                "similarity": similarity if similar_exp else 0,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
