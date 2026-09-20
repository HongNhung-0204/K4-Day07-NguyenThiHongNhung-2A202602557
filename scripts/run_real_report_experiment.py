from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chunking import FixedSizeChunker, compute_similarity
from src.embeddings import OPENAI_EMBEDDING_MODEL, OpenAIEmbedder
from src.models import Document
from src.store import EmbeddingStore


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "shopee-return-refund"
CHUNKER = FixedSizeChunker(chunk_size=500, overlap=50)

SIMILARITY_PAIRS = [
    ("Người mua có 15 ngày để gửi yêu cầu trả hàng.", "Thời hạn yêu cầu trả hàng của người mua là 15 ngày."),
    ("Shopee hoàn tiền qua ShopeePay trong 24 giờ.", "Tiền hoàn được gửi vào ví ShopeePay sau một ngày."),
    ("Sản phẩm bị lỗi và không hoạt động.", "Hôm nay trời có mưa lớn."),
    ("Người mua cần quay video mở kiện hàng.", "Sản phẩm cần được đóng gói bằng hộp carton."),
    ("Hoàn tiền khi nhận hàng.", "Người bán đăng sản phẩm mới lên cửa hàng."),
]

QUERIES = [
    "Thời hạn gửi yêu cầu với thực phẩm tươi sống?",
    "Đơn người bán tự vận chuyển có thời hạn bao nhiêu ngày?",
    "Mở hộp kiểm tra có được trả hàng do đổi ý không?",
    "Cần bằng chứng gì khi nhận hàng bị lỗi?",
    "Hoàn tiền qua ShopeePay mất bao lâu?",
]


def load_store(embedder: OpenAIEmbedder) -> EmbeddingStore:
    store = EmbeddingStore(collection_name="real_report_experiment", embedding_fn=embedder)
    documents = []
    for path in sorted(DATA_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        front_matter, content = raw.split("---", 2)[1:]
        metadata = {"doc_id": path.stem, "source": str(path)}
        for line in front_matter.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip('"')
        for index, chunk in enumerate(CHUNKER.chunk(content.strip())):
            chunk_metadata = dict(metadata)
            chunk_metadata["chunk_index"] = index
            documents.append(Document(f"{path.stem}#{index}", chunk, chunk_metadata))
    store.add_documents(documents)
    print(f"Loaded {len(documents)} chunks from {len(list(DATA_DIR.glob('*.md')))} files.")
    return store


def main() -> None:
    load_dotenv(ROOT / ".env")
    model_name = os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
    embedder = OpenAIEmbedder(model_name=model_name)
    print(f"Backend: {embedder._backend_name}")

    print("\n=== Similarity ===")
    for index, (sentence_a, sentence_b) in enumerate(SIMILARITY_PAIRS, 1):
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        print(f"{index}. {score:.4f} | A: {sentence_a} | B: {sentence_b}")

    store = load_store(embedder)
    print("\n=== Retrieval top-3 ===")
    for index, query in enumerate(QUERIES, 1):
        print(f"\nQ{index}: {query}")
        for rank, result in enumerate(store.search(query, top_k=3), 1):
            metadata = result["metadata"]
            print(
                f"  {rank}. {metadata['doc_id']}#{metadata['chunk_index']} "
                f"score={result['score']:.4f}"
            )
            print(f"     {result['content'][:180].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    main()
