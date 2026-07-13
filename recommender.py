import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

INDEX = faiss.read_index(
    os.path.join(BASE_DIR, "odoo_modules_index.faiss")
)

with open(
    os.path.join(BASE_DIR, "merged_modules.json"),
    "r",
    encoding="utf-8"
) as f:
    MODULES = json.load(f)


def search(requirement, top_k=5):

    embedding = MODEL.encode(
        requirement,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    embedding = embedding.astype(np.float32).reshape(1, -1)

    scores, ids = INDEX.search(embedding, top_k)

    results = []

    for score, idx in zip(scores[0], ids[0]):

        if idx == -1:
            continue

        module = MODULES[idx]

        results.append({
            "title": module.get("Title", ""),
            "source": module.get("Source", ""),
            "category": module.get("Category", ""),
            "summary": module.get("Summary", ""),
            "features": module.get("Features", ""),
            "url": module.get("URL", ""),
            "score": round(float(score) * 100, 2)
        })

    return results