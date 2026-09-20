from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chunking import compute_similarity
from src.embeddings import OpenAIEmbedder, OPENAI_EMBEDDING_MODEL


sentence_a = "Người mua có 15 ngày để gửi yêu cầu trả hàng."
sentence_b = "Thời hạn yêu cầu trả hàng của người mua là 15 ngày."

load_dotenv()
embedder = OpenAIEmbedder(
	model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
)
vector_a = embedder(sentence_a)
vector_b = embedder(sentence_b)
score = compute_similarity(vector_a, vector_b)

print(f"Backend: {embedder._backend_name}")
print(f"Embedding dimension: {len(vector_a)}")
print(f"Sentence A: {sentence_a}")
print(f"Sentence B: {sentence_b}")
print(f"Cosine similarity: {score:.4f}")
