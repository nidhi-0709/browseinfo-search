import faiss
import numpy as np
import os


# Paths

EMBEDDING_FILE = "odoo_module_embeddings.npy"

INDEX_FILE = "odoo_modules_index.faiss"



print("Loading embeddings...")

embeddings = np.load(
    EMBEDDING_FILE
)


print(
    "Embedding shape:",
    embeddings.shape
)


# Convert to float32
embeddings = embeddings.astype(
    "float32"
)


# Normalize for cosine similarity

faiss.normalize_L2(
    embeddings
)


dimension = embeddings.shape[1]


# Create FAISS index

index = faiss.IndexFlatIP(
    dimension
)


# Add vectors

index.add(
    embeddings
)


print(
    "Total vectors:",
    index.ntotal
)


# Save index

faiss.write_index(
    index,
    INDEX_FILE
)


print(
    "FAISS index created successfully"
)