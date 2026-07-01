"""Vektor-Store (ChromaDB) für Typen 3/4 – semantisches Retrieval.
Bei Ablation 'ohne dualen Store' (H5) landet ALLES hier."""
from __future__ import annotations
import chromadb
from src.models import MemoryItem


class VectorStore:
    def __init__(self, path: str, embed_fn):
        self.client = chromadb.PersistentClient(path=path)
        self.col = self.client.get_or_create_collection("memories")
        self.embed = embed_fn

    def add(self, it: MemoryItem) -> None:
        self.col.upsert(ids=[it.id], embeddings=[self.embed(it.content)],
                        documents=[it.content], metadatas=[it.to_metadata()])

    def query(self, text: str, top_k: int, where: dict | None = None):
        res = self.col.query(query_embeddings=[self.embed(text)], n_results=top_k,
                             where=where or None)
        out = []
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0],
                                   res["distances"][0]):
            out.append({"document": doc, "metadata": meta, "similarity": 1 - dist})
        return out

    def delete(self, mem_id: str) -> None:
        self.col.delete(ids=[mem_id])
