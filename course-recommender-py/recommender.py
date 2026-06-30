import re

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
# model = SentenceTransformer('distiluse-base-multilingual-cased-v2', device='cpu')

course_db = {}

macedonian_stopwords = {
    'и', 'во', 'на', 'со', 'да', 'се', 'од', 'за', 'не', 'го', 'ја', 'тие', 'тоа', 'ова',
    'кој', 'што', 'каде', 'како', 'кога', 'зошто', 'е', 'сум', 'си', 'беше', 'биде',
    'ни', 'ви', 'ги', 'им', 'му', 'ѝ', 'низ', 'преку', 'до', 'кон', 'без', 'по'
}


@app.route("/load_courses", methods=["POST"])
def load_courses():
    global course_db
    data = request.get_json()
    courses = data["courses"]

    texts = [preprocess(course["text"]) for course in courses]
    codes = [course["code"] for course in courses]

    embeddings = model.encode(texts, convert_to_tensor=True)

    course_db = {
        code: {"text": text, "embedding": emb}
        for code, text, emb in zip(codes, texts, embeddings)
    }

    return jsonify({"status": "loaded", "count": len(course_db)})


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    selected_codes = data["selected_codes"]

    selected_embeddings = [course_db[code]["embedding"] for code in selected_codes if code in course_db]
    if not selected_embeddings:
        return jsonify({"error": "No valid course codes found"}), 400

    query_embedding = sum(selected_embeddings) / len(selected_embeddings)

    results = []
    for code, course in course_db.items():
        if code in selected_codes:
            continue
        score = util.cos_sim(query_embedding, course["embedding"])[0].item()
        results.append({"code": code, "score": score})

    results.sort(key=lambda x: -x["score"])
    return jsonify(results)


def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^а-шА-Шa-zA-Z0-9\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in macedonian_stopwords]
    return " ".join(tokens)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
