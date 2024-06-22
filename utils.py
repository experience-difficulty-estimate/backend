import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(input=text, model="text-embedding-3-large")
    return response.data[0].embedding


def get_difficulty_scores(experience: str) -> list[float]:
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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        max_tokens=100,
        messages=[
            {"role": "system", "content": INITIAL_PROMPT},
            {"role": "user", "content": f"Estimate the difficulty of: {experience}"},
        ],
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)
