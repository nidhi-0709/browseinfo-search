import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ==========================================================
# Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INDEX_FILE = os.path.join(BASE_DIR, "odoo_modules_index.faiss")
DATA_FILE = os.path.join(BASE_DIR, "merged_modules.json")

# ==========================================================
# Load Model
# ==========================================================

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# ==========================================================
# Load FAISS Index
# ==========================================================

INDEX = faiss.read_index(INDEX_FILE)

# ==========================================================
# Load Modules
# ==========================================================

with open(DATA_FILE, "r", encoding="utf-8") as f:
    MODULES = json.load(f)

# ==========================================================
# Search Function
# ==========================================================

def search(requirement, similarity_threshold=35):

    # Generate embedding
    embedding = MODEL.encode(
        requirement,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    embedding = embedding.astype(np.float32).reshape(1, -1)

    # Search ALL modules
    scores, ids = INDEX.search(embedding, len(MODULES))

    results = []
    seen = set()

    for score, idx in zip(scores[0], ids[0]):

        if idx == -1:
            continue

        similarity = round(float(score) * 100, 2)

        # Ignore weak matches
        if similarity < similarity_threshold:
            continue

        module = MODULES[idx]

        title = module.get("Title", "")

        # Avoid duplicate modules
        if title in seen:
            continue

        seen.add(title)

        results.append({
            "title": title,
            "source": module.get("Source", ""),
            "category": module.get("Category", ""),
            "summary": module.get("Summary", ""),
            "features": module.get("Features", ""),
            "url": module.get("URL", ""),
            "score": similarity
        })

    # Sort by similarity
    results.sort(key=lambda x: x["score"], reverse=True)

    return results