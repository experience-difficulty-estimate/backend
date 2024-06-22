from .utils import get_embedding, get_difficulty_scores, find_similar_experience
from .models import get_db_connection
import json
import numpy as np


def estimate_difficulty(experience):
    try:
        embedding = get_embedding(experience)
        similar_exp, similarity = find_similar_experience(embedding)

        if similar_exp and similarity > 0.95:
            difficulty_scores = json.loads(similar_exp["difficulty_scores"])
        else:
            difficulty_scores = get_difficulty_scores(experience)

        total_difficulty = sum(difficulty_scores) / len(difficulty_scores)
        level = int(total_difficulty / 10) + 1

        # 데이터베이스에 저장
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO experiences (text, embedding, difficulty_scores) VALUES (?, ?, ?)",
            (experience, np.array(embedding).tobytes(), json.dumps(difficulty_scores)),
        )
        conn.commit()
        conn.close()

        return {
            "experience": experience,
            "difficulty_scores": difficulty_scores,
            "total_difficulty": total_difficulty,
            "level": level,
            "similarity": similarity if similar_exp else 0,
        }
    except Exception as e:
        return {"error": str(e)}
