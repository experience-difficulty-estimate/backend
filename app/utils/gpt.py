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


def get_single_difficulty_score(experience: str) -> float:
    PROMPT = """You are an AI assistant specialized in estimating the overall difficulty of various life experiences. You will receive a description of an experience and should respond with a single difficulty score.

    Provide a score from 0 to 100, where 0 is extremely easy/common and 100 is extremely difficult/rare.

    Consider factors like physical difficulty, mental effort, time investment, technical complexity, social challenge, financial burden, risk level, persistence required, creativity needed, and rarity.

    Your response should be a single number between 0 and 100, with up to two decimal places. Do not include any additional text or explanation."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        max_tokens=10,
        messages=[
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": f"Estimate the overall difficulty of: {experience}",
            },
        ],
        temperature=0.7,
    )
    return float(response.choices[0].message.content.strip())


def analyze_experience(experience: str) -> dict:
    single_score = get_single_difficulty_score(experience)
    detailed_scores = get_difficulty_scores(experience)

    return {"single_score": single_score, "detailed_scores": detailed_scores}


def compare_experience_difficulties(
    new_experience: str, existing_experience: str, existing_score: float
) -> float:
    PROMPT = f"""Compare the difficulty of two experiences. The first experience has a known difficulty score of {existing_score} out of 100.

    Experience 1 (Score: {existing_score}): {existing_experience}
    Experience 2 (Unknown Score): {new_experience}

    Estimate the difficulty score for Experience 2 relative to Experience 1. Your response should be a single number between 0 and 100, with up to two decimal places. Do not include any additional text or explanation."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        max_tokens=10,
        messages=[
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": "What is the estimated difficulty score for Experience 2?",
            },
        ],
        temperature=0.7,
    )
    return float(response.choices[0].message.content.strip())
