from groq import Groq
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.prompts import workout_prompt

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def generate_workout(age, height, weight, goal, experience, workout_type, diet, calories, protein):

    prompt = workout_prompt(
        age, height, weight, goal,
        experience, workout_type, diet,
        calories, protein
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=701
    )

    return response.choices[0].message.content


def retrieve_knowledge(question):

    docs = []
    knowledge_folder = "knowledge"

    for filename in os.listdir(knowledge_folder):
        with open(os.path.join(knowledge_folder, filename), "r", encoding="utf-8") as f:
            docs.append(f.read())

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(docs + [question])

    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    best_doc = docs[similarities.argmax()]

    return best_doc


def ask_coach(question):

    context = retrieve_knowledge(question)

    prompt = f"""
You are TrainWise AI, an expert AI fitness coach.

Use this knowledge context:

{context}

Answer clearly, practically, and accurately.

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=600
    )

    return response.choices[0].message.content
