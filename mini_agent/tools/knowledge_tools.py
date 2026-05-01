"""Knowledge and RAG tools for the BPS Academic Research Agent.

Provides tools for:
- chunk_document: Split documents into chunks for embedding
- embed_papers: Embed papers using sentence-transformers or TF-IDF
- vector_search: Search embedded papers/chunks using cosine similarity
- extract_entities: Extract named entities from text
- build_knowledge_graph: Build knowledge graph from papers
- query_knowledge_graph: Query the knowledge graph
- paper_qa: Answer questions using embedded papers with citations
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import numpy as np

    _HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore[assignment]
    _HAS_NUMPY = False

from .base import Tool, ToolResult


def _require_numpy() -> ToolResult | None:
    """Return an error ToolResult if numpy is not installed, else None."""
    if not _HAS_NUMPY:
        return ToolResult(
            success=False,
            error=("numpy is required for knowledge tools. Install with: pip install 'bps-stat-agent[research-core]'"),
        )
    return None


# ---------------------------------------------------------------------------
# Optional dependency availability flags
# ---------------------------------------------------------------------------

_HAS_SENTENCE_TRANSFORMERS = False
_HAS_LANCEDB = False
_HAS_SCISPACY = False
_HAS_SPACY = False
_HAS_PAPER_QA = False
_HAS_NETWORKX = False
_HAS_SKLEARN = False
_HAS_CHONKIE = False

try:
    from sentence_transformers import SentenceTransformer

    _HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    pass

try:
    import lancedb

    _HAS_LANCEDB = True
except ImportError:
    pass

try:
    import spacy

    _HAS_SPACY = True
except ImportError:
    pass

try:
    import scispacy  # noqa: F401

    _HAS_SCISPACY = True
except ImportError:
    pass

try:
    from paper_qa import Docs

    _HAS_PAPER_QA = True
except ImportError:
    pass

try:
    import networkx as nx

    _HAS_NETWORKX = True
except ImportError:
    pass

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine

    _HAS_SKLEARN = True
except ImportError:
    pass

try:
    import chonkie  # noqa: F401

    _HAS_CHONKIE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into chunks by sentences with overlap.

    Args:
        text: Input text to chunk.
        chunk_size: Target chunk size in characters.
        overlap: Number of characters to overlap between chunks.

    Returns:
        List of text chunks.
    """
    if not text.strip():
        return []

    import re

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_chunk: list[str] = []
    current_len = 0

    for sentence in sentences:
        sent_len = len(sentence)
        if current_len + sent_len > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            overlap_text = " ".join(current_chunk)
            if len(overlap_text) > overlap:
                keep_sentences: list[str] = []
                keep_len = 0
                for s in reversed(current_chunk):
                    if keep_len + len(s) <= overlap:
                        keep_sentences.insert(0, s)
                        keep_len += len(s) + 1
                    else:
                        break
                current_chunk = keep_sentences
                current_len = keep_len
            else:
                current_chunk = []
                current_len = 0
        current_chunk.append(sentence)
        current_len += sent_len + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def _read_text_file(path: Path) -> str:
    """Read text from a file, with basic PDF extraction support."""
    if path.suffix.lower() == ".pdf":
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(str(path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            try:
                from pdfminer.high_level import extract_text

                return extract_text(str(path))
            except ImportError:
                try:
                    from PyPDF2 import PdfReader

                    reader = PdfReader(str(path))
                    pages: list[str] = []
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            pages.append(t)
                    return "\n\n".join(pages)
                except ImportError:
                    return ""
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


def _simple_sentence_split(text: str) -> list[str]:
    """Split text into sentences using a simple regex heuristic."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [s.strip() for s in sentences if s.strip()]


def _estimate_tokens(text: str) -> int:
    """Rough token count estimate (~1 token per 4 characters for English)."""
    return max(1, len(text) // 4)


# ===================================================================
# 1. ChunkDocumentTool
# ===================================================================


class ChunkDocumentTool(Tool):
    """Split a document into smaller chunks for embedding and RAG.

    Supports three chunking methods:
    - **semantic**: Uses chonkie for semantically coherent chunks (preferred)
    - **fixed**: Simple word-count-based splitting with overlap
    - **sentence**: Splits on sentence boundaries, then groups to target size
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "chunk_document"

    @property
    def description(self) -> str:
        return (
            "Split a document into smaller chunks suitable for embedding or RAG. "
            "Methods: 'semantic' (chonkie-based coherent chunks), 'fixed' "
            "(word-count-based with overlap), 'sentence' (sentence-boundary "
            "splitting). Saves chunks as JSON to the knowledge/ directory."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the document to chunk (relative to workspace or absolute)",
                },
                "chunk_size": {
                    "type": "integer",
                    "description": "Target chunk size in tokens (default: 512)",
                },
                "overlap": {
                    "type": "integer",
                    "description": "Overlap between chunks in tokens (default: 50)",
                },
                "method": {
                    "type": "string",
                    "enum": ["semantic", "fixed", "sentence"],
                    "description": "Chunking method (default: semantic)",
                },
            },
            "required": ["file_path"],
        }

    async def execute(
        self,
        file_path: str,
        chunk_size: int = 512,
        overlap: int = 50,
        method: str = "semantic",
        **kwargs: Any,
    ) -> ToolResult:
        """Chunk a document into smaller pieces for embedding."""
        if (err := _require_numpy()) is not None:
            return err
        workspace = Path(self._workspace_dir)
        full_path = Path(file_path) if Path(file_path).is_absolute() else workspace / file_path

        if not full_path.exists():
            return ToolResult(success=False, error=f"File not found: {full_path}")

        text = _read_text_file(full_path)
        if not text.strip():
            return ToolResult(success=False, error=f"Could not extract text from {full_path.name}")

        if overlap >= chunk_size:
            return ToolResult(
                success=False,
                error=f"overlap ({overlap}) must be less than chunk_size ({chunk_size})",
            )

        chunks: list[dict[str, Any]] = []

        if method == "semantic":
            chunks = self._chunk_semantic(text, chunk_size, overlap)
        elif method == "sentence":
            chunks = self._chunk_sentence(text, chunk_size, overlap)
        else:
            chunks = self._chunk_fixed(text, chunk_size, overlap)

        if not chunks:
            return ToolResult(success=False, error="Chunking produced no output")

        # Attach source metadata to each chunk
        for chunk in chunks:
            chunk["source_file"] = full_path.name
            chunk["source_path"] = str(full_path)

        # Save chunks to knowledge/ directory
        output_dir = workspace / "knowledge"
        output_dir.mkdir(parents=True, exist_ok=True)
        chunks_file = output_dir / f"{full_path.stem}_chunks.json"
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        total_tokens = sum(c.get("token_count", 0) for c in chunks)
        result = {
            "file": full_path.name,
            "method": method,
            "num_chunks": len(chunks),
            "total_tokens": total_tokens,
            "avg_chunk_tokens": total_tokens // max(len(chunks), 1),
            "output_path": str(chunks_file),
            "preview": [
                {
                    "index": c["index"],
                    "token_count": c["token_count"],
                    "text_preview": c["text"][:120] + "..." if len(c["text"]) > 120 else c["text"],
                }
                for c in chunks[:5]
            ],
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))

    def _chunk_semantic(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Semantic chunking using chonkie, with sentence fallback."""
        if _HAS_CHONKIE:
            try:
                from chonkie import TokenChunker

                chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=overlap)
                raw_chunks = chunker.chunk(text)
                chunks: list[dict[str, Any]] = []
                for i, chunk in enumerate(raw_chunks):
                    chunk_text = chunk.text if hasattr(chunk, "text") else str(chunk)
                    token_count = chunk.token_count if hasattr(chunk, "token_count") else _estimate_tokens(chunk_text)
                    chunks.append(
                        {
                            "index": i,
                            "text": chunk_text,
                            "token_count": token_count,
                        }
                    )
                return chunks
            except Exception:
                pass
        # Fallback to sentence-based splitting
        return self._chunk_sentence(text, chunk_size, overlap)

    def _chunk_sentence(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Split on sentence boundaries, then group to target size."""
        sentences = _simple_sentence_split(text)
        if not sentences:
            return self._chunk_fixed(text, chunk_size, overlap)

        chunks: list[dict[str, Any]] = []
        current_sentences: list[str] = []
        current_tokens = 0

        for sentence in sentences:
            sent_tokens = _estimate_tokens(sentence)
            if current_tokens + sent_tokens > chunk_size and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append(
                    {
                        "index": len(chunks),
                        "text": chunk_text,
                        "token_count": _estimate_tokens(chunk_text),
                    }
                )
                # Keep overlap sentences
                overlap_tokens = 0
                overlap_sents: list[str] = []
                for s in reversed(current_sentences):
                    st = _estimate_tokens(s)
                    if overlap_tokens + st > overlap:
                        break
                    overlap_sents.insert(0, s)
                    overlap_tokens += st
                current_sentences = overlap_sents
                current_tokens = overlap_tokens

            current_sentences.append(sentence)
            current_tokens += sent_tokens

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append(
                {
                    "index": len(chunks),
                    "text": chunk_text,
                    "token_count": _estimate_tokens(chunk_text),
                }
            )

        return chunks

    def _chunk_fixed(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Simple word-count-based splitting with overlap."""
        words = text.split()
        words_per_chunk = max(1, int(chunk_size * 0.75))
        overlap_words = max(0, int(overlap * 0.75))

        chunks: list[dict[str, Any]] = []
        pos = 0
        while pos < len(words):
            end = min(pos + words_per_chunk, len(words))
            chunk_text = " ".join(words[pos:end])
            chunks.append(
                {
                    "index": len(chunks),
                    "text": chunk_text,
                    "token_count": _estimate_tokens(chunk_text),
                }
            )
            step = max(1, words_per_chunk - overlap_words)
            pos += step

        return chunks


# ===================================================================
# 2. EmbedPapersTool
# ===================================================================


class EmbedPapersTool(Tool):
    """Embed all papers in a directory using sentence-transformers or TF-IDF."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "embed_papers"

    @property
    def description(self) -> str:
        return (
            "Embed all papers in a directory for vector search. Uses "
            "sentence-transformers (default: all-MiniLM-L6-v2) when available, "
            "falls back to TF-IDF vectorization. Saves embeddings to the "
            "embeddings/ directory in the workspace."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "papers_dir": {
                    "type": "string",
                    "description": "Directory containing papers (default: literature/papers/)",
                },
                "model": {
                    "type": "string",
                    "description": "Embedding model name (default: all-MiniLM-L6-v2)",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        papers_dir: str = "literature/papers/",
        model: str = "all-MiniLM-L6-v2",
        **kwargs: Any,
    ) -> ToolResult:
        """Embed papers and store vectors."""
        if (err := _require_numpy()) is not None:
            return err
        workspace = Path(self._workspace_dir)
        full_papers_dir = Path(papers_dir) if Path(papers_dir).is_absolute() else workspace / papers_dir

        if not full_papers_dir.exists():
            full_papers_dir.mkdir(parents=True, exist_ok=True)
            return ToolResult(
                success=False,
                error=f"Papers directory {full_papers_dir} is empty. Add papers first.",
            )

        paper_files = (
            list(full_papers_dir.glob("*.pdf"))
            + list(full_papers_dir.glob("*.txt"))
            + list(full_papers_dir.glob("*.md"))
        )
        if not paper_files:
            return ToolResult(
                success=False,
                error=f"No papers found in {full_papers_dir}. Add .pdf, .txt, or .md files.",
            )

        embeddings_dir = workspace / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)

        # Read all papers and chunk them
        all_chunks: list[dict[str, Any]] = []
        paper_metadata: list[dict[str, Any]] = []

        for paper_path in paper_files:
            text = _read_text_file(paper_path)
            if not text.strip():
                continue

            paper_id = len(paper_metadata)
            paper_metadata.append(
                {
                    "paper_id": paper_id,
                    "path": str(paper_path),
                    "filename": paper_path.name,
                    "text_preview": text[:500],
                }
            )

            # Chunk the paper
            words = text.split()
            chunk_size_words = 384
            overlap_words = 48
            start = 0
            chunk_idx = 0
            while start < len(words):
                end = min(start + chunk_size_words, len(words))
                chunk_text = " ".join(words[start:end])
                all_chunks.append(
                    {
                        "chunk_id": chunk_idx,
                        "paper_id": paper_id,
                        "paper_filename": paper_path.name,
                        "text": chunk_text,
                        "start_word": start,
                        "end_word": end,
                    }
                )
                chunk_idx += 1
                start += chunk_size_words - overlap_words

        if not paper_metadata:
            return ToolResult(success=False, error="No papers could be read from the directory")

        chunk_texts = [c["text"] for c in all_chunks]
        embedding_method = "none"
        chunk_emb_array = np.array([])
        paper_emb_array = np.array([])

        # Try sentence-transformers first
        if _HAS_SENTENCE_TRANSFORMERS:
            try:
                st_model = SentenceTransformer(model)
                embedding_method = f"sentence-transformers ({model})"

                # Paper-level embeddings (from first 2000 chars)
                paper_texts = [m["text_preview"] for m in paper_metadata]
                paper_emb_array = st_model.encode(paper_texts)

                # Chunk-level embeddings
                if chunk_texts:
                    chunk_emb_array = st_model.encode(chunk_texts)
            except Exception:
                embedding_method = "none"

        # Fallback to TF-IDF
        if embedding_method == "none":
            if not _HAS_SKLEARN:
                return ToolResult(
                    success=False,
                    error=(
                        "No embedding backend available. Install one of:\n"
                        "  pip install sentence-transformers\n"
                        "  pip install scikit-learn"
                    ),
                )
            embedding_method = "tfidf"
            vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")

            if chunk_texts:
                chunk_emb_array = vectorizer.fit_transform(chunk_texts).toarray()

            paper_texts = [m["text_preview"] for m in paper_metadata]
            if paper_texts:
                paper_vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
                paper_emb_array = paper_vectorizer.fit_transform(paper_texts).toarray()

        # Save embeddings
        storage_info: dict[str, Any] = {}

        if _HAS_LANCEDB and chunk_emb_array.ndim == 2 and chunk_emb_array.shape[0] > 0:
            try:
                db = lancedb.connect(str(embeddings_dir / "lancedb"))
                paper_records = [
                    {"vector": paper_emb_array[i].tolist(), **meta}
                    for i, meta in enumerate(paper_metadata)
                    if i < len(paper_emb_array)
                ]
                if paper_records:
                    db.create_table("papers", paper_records, mode="overwrite")

                chunk_records = [
                    {"vector": chunk_emb_array[i].tolist(), **chunk}
                    for i, chunk in enumerate(all_chunks)
                    if i < len(chunk_emb_array)
                ]
                if chunk_records:
                    db.create_table("chunks", chunk_records, mode="overwrite")

                storage_info = {"backend": "lancedb", "path": str(embeddings_dir / "lancedb")}
            except Exception:
                storage_info = self._save_numpy(
                    embeddings_dir,
                    paper_emb_array,
                    chunk_emb_array,
                    paper_metadata,
                    all_chunks,
                )
        else:
            storage_info = self._save_numpy(
                embeddings_dir,
                paper_emb_array,
                chunk_emb_array,
                paper_metadata,
                all_chunks,
            )

        result = {
            "embedded_papers": len(paper_metadata),
            "total_chunks": len(all_chunks),
            "embedding_method": embedding_method,
            "embedding_dim": (
                int(chunk_emb_array.shape[1]) if chunk_emb_array.ndim == 2 and chunk_emb_array.shape[0] > 0 else 0
            ),
            "storage": storage_info,
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))

    @staticmethod
    def _save_numpy(
        store_path: Path,
        paper_emb: np.ndarray,
        chunk_emb: np.ndarray,
        paper_meta: list[dict[str, Any]],
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Save embeddings as numpy arrays with JSON metadata."""
        if paper_emb.ndim == 2 and paper_emb.shape[0] > 0:
            np.save(str(store_path / "paper_embeddings.npy"), paper_emb)
        if chunk_emb.ndim == 2 and chunk_emb.shape[0] > 0:
            np.save(str(store_path / "chunk_embeddings.npy"), chunk_emb)

        with open(store_path / "paper_metadata.json", "w") as f:
            json.dump(paper_meta, f, indent=2)
        with open(store_path / "chunk_metadata.json", "w") as f:
            json.dump(chunks, f, indent=2)

        return {"backend": "numpy", "path": str(store_path)}


# ===================================================================
# 3. VectorSearchTool
# ===================================================================


class VectorSearchTool(Tool):
    """Search embedded papers/chunks using cosine similarity."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "vector_search"

    @property
    def description(self) -> str:
        return (
            "Search embedded papers and text chunks using vector similarity. "
            "Uses LanceDB when available, otherwise falls back to numpy-based "
            "cosine similarity on saved embeddings. Returns ranked results "
            "with similarity scores and source information."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query text",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                },
                "filter_metadata": {
                    "type": "object",
                    "description": 'Optional metadata filters (e.g. {"paper_filename": "paper1.pdf"})',
                },
            },
            "required": ["query"],
        }

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Search embedded papers/chunks."""
        if (err := _require_numpy()) is not None:
            return err
        workspace = Path(self._workspace_dir)
        embeddings_dir = workspace / "embeddings"

        if not embeddings_dir.exists():
            return ToolResult(
                success=False,
                error="Embeddings directory not found. Run embed_papers first.",
            )

        # Encode query
        query_embedding: np.ndarray | None = None

        if _HAS_SENTENCE_TRANSFORMERS:
            try:
                model = SentenceTransformer("all-MiniLM-L6-v2")
                query_embedding = model.encode([query])[0]
            except Exception:
                pass

        # Try LanceDB search
        lancedb_path = embeddings_dir / "lancedb"
        if _HAS_LANCEDB and lancedb_path.exists() and query_embedding is not None:
            try:
                results = self._search_lancedb(lancedb_path, query_embedding, top_k, filter_metadata)
                if results:
                    output = {
                        "query": query,
                        "num_results": len(results),
                        "backend": "lancedb",
                        "results": results,
                    }
                    return ToolResult(success=True, content=json.dumps(output, indent=2))
            except Exception:
                pass

        # Numpy-based search
        if query_embedding is not None:
            results = self._search_numpy_embeddings(embeddings_dir, query_embedding, top_k, filter_metadata)
        elif _HAS_SKLEARN:
            results = self._search_tfidf(embeddings_dir, query, top_k, filter_metadata)
        else:
            return ToolResult(
                success=False,
                error=(
                    "No search backend available. Install one of:\n"
                    "  pip install sentence-transformers\n"
                    "  pip install scikit-learn"
                ),
            )

        if not results:
            return ToolResult(
                success=True,
                content=json.dumps({"query": query, "results": [], "message": "No results found"}),
            )

        output = {
            "query": query,
            "num_results": len(results),
            "backend": "numpy" if query_embedding is not None else "tfidf",
            "results": results,
        }
        return ToolResult(success=True, content=json.dumps(output, indent=2))

    @staticmethod
    def _search_lancedb(
        store_path: Path,
        query_emb: np.ndarray,
        top_k: int,
        filter_metadata: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Search using LanceDB."""
        results: list[dict[str, Any]] = []
        db = lancedb.connect(str(store_path))
        tables = db.table_names()

        if "chunks" in tables:
            tbl = db.open_table("chunks")
            query_result = tbl.search(query_emb.tolist()).limit(top_k).to_list()
            for row in query_result:
                entry: dict[str, Any] = {
                    "type": "chunk",
                    "score": float(1.0 / (1.0 + row.get("_distance", 0))),
                    "text": row.get("text", "")[:500],
                    "paper_filename": row.get("paper_filename", ""),
                    "chunk_id": row.get("chunk_id", -1),
                }
                if filter_metadata:
                    if all(row.get(k) == v for k, v in filter_metadata.items()):
                        results.append(entry)
                else:
                    results.append(entry)

        if "papers" in tables and len(results) < top_k:
            tbl = db.open_table("papers")
            query_result = tbl.search(query_emb.tolist()).limit(top_k).to_list()
            for row in query_result:
                results.append(
                    {
                        "type": "paper",
                        "score": float(1.0 / (1.0 + row.get("_distance", 0))),
                        "filename": row.get("filename", ""),
                        "text_preview": row.get("text_preview", "")[:300],
                        "path": row.get("path", ""),
                    }
                )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _search_numpy_embeddings(
        store_path: Path,
        query_emb: np.ndarray,
        top_k: int,
        filter_metadata: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Search using numpy cosine similarity on saved embeddings."""
        results: list[dict[str, Any]] = []

        chunk_emb_path = store_path / "chunk_embeddings.npy"
        chunk_meta_path = store_path / "chunk_metadata.json"
        if chunk_emb_path.exists() and chunk_meta_path.exists():
            chunk_embs = np.load(str(chunk_emb_path))
            with open(chunk_meta_path) as f:
                chunk_meta = json.load(f)

            for i, emb in enumerate(chunk_embs):
                score = _cosine_similarity(query_emb, emb)
                meta = chunk_meta[i] if i < len(chunk_meta) else {}

                if filter_metadata and not all(meta.get(k) == v for k, v in filter_metadata.items()):
                    continue

                results.append(
                    {
                        "type": "chunk",
                        "score": score,
                        "text": meta.get("text", "")[:500],
                        "paper_filename": meta.get("paper_filename", ""),
                        "chunk_id": meta.get("chunk_id", -1),
                    }
                )

        paper_emb_path = store_path / "paper_embeddings.npy"
        paper_meta_path = store_path / "paper_metadata.json"
        if paper_emb_path.exists() and paper_meta_path.exists():
            paper_embs = np.load(str(paper_emb_path))
            with open(paper_meta_path) as f:
                paper_meta = json.load(f)

            for i, emb in enumerate(paper_embs):
                score = _cosine_similarity(query_emb, emb)
                meta = paper_meta[i] if i < len(paper_meta) else {}
                results.append(
                    {
                        "type": "paper",
                        "score": score,
                        "filename": meta.get("filename", ""),
                        "text_preview": meta.get("text_preview", "")[:300],
                        "path": meta.get("path", ""),
                    }
                )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _search_tfidf(
        store_path: Path,
        query_text: str,
        top_k: int,
        filter_metadata: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Search using TF-IDF when no embedding model is available."""
        chunk_meta_path = store_path / "chunk_metadata.json"
        if not chunk_meta_path.exists():
            return []

        with open(chunk_meta_path) as f:
            chunk_meta = json.load(f)

        texts = [c.get("text", "") for c in chunk_meta]
        if not texts:
            return []

        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(texts)
        query_vec = vectorizer.transform([query_text])
        similarities = sklearn_cosine(query_vec, tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]
        results: list[dict[str, Any]] = []
        for idx in top_indices:
            if similarities[idx] < 0.01:
                break
            meta = chunk_meta[idx] if idx < len(chunk_meta) else {}
            if filter_metadata and not all(meta.get(k) == v for k, v in filter_metadata.items()):
                continue
            results.append(
                {
                    "type": "chunk",
                    "score": float(similarities[idx]),
                    "text": meta.get("text", "")[:500],
                    "paper_filename": meta.get("paper_filename", ""),
                    "chunk_id": meta.get("chunk_id", -1),
                }
            )

        return results


# ===================================================================
# 4. ExtractEntitiesTool
# ===================================================================


class ExtractEntitiesTool(Tool):
    """Extract named entities from text using NER or regex fallback."""

    _PATTERNS: dict[str, re.Pattern[str]] = {
        "DATE": re.compile(
            r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
            r"(?:January|February|March|April|May|June|July|August|September|"
            r"October|November|December)\s+\d{1,2},?\s+\d{4})\b",
            re.IGNORECASE,
        ),
        "DOI": re.compile(r"\b(10\.\d{4,}/[^\s,;\"']+)\b"),
        "PERCENTAGE": re.compile(r"\b\d+(?:\.\d+)?%\b"),
        "ORGANIZATION": re.compile(
            r"\b(?:BPS|World Bank|IMF|UNDP|UNESCO|WHO|OECD|ADB|"
            r"Bank Indonesia|Bappenas|Kementerian|Ministry of|"
            r"University of|Institut|Universitas)\b(?:\s+[A-Z][a-z]+)*",
        ),
        "METHOD": re.compile(
            r"\b(?:PCR|ELISA|Western blot|mass spectrometry|chromatography|"
            r"regression|ANOVA|t-test|chi-square|meta-analysis|"
            r"machine learning|deep learning|neural network|"
            r"SEM|OLS|GMM|VAR|VECM|panel data|difference-in-differences|"
            r"instrumental variable|propensity score|randomized control|"
            r"logistic regression|Bayesian|Monte Carlo|bootstrap)\b",
            re.IGNORECASE,
        ),
        "METRIC": re.compile(
            r"\b(?:p-value|confidence interval|R-squared|R²|AIC|BIC|"
            r"RMSE|MAE|F-statistic|odds ratio|hazard ratio|"
            r"sensitivity|specificity|precision|recall|accuracy|"
            r"GDP|GNI|HDI|IPM|Gini|poverty rate|inflation rate|"
            r"unemployment rate|CPI|PDB)\b",
            re.IGNORECASE,
        ),
        "CHEMICAL": re.compile(
            r"\b(?:sodium|potassium|calcium|chloride|sulfate|nitrate|"
            r"phosphate|glucose|ethanol|methanol|acetone|benzene|toluene)\b",
            re.IGNORECASE,
        ),
        "DISEASE": re.compile(
            r"\b(?:diabetes|cancer|hypertension|obesity|malaria|tuberculosis|"
            r"HIV|AIDS|COVID-19|SARS|influenza|pneumonia|asthma|arthritis|"
            r"alzheimer|parkinson|hepatitis|anemia|dengue|cholera|stunting)\b",
            re.IGNORECASE,
        ),
    }

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "extract_entities"

    @property
    def description(self) -> str:
        return (
            "Extract named entities from text. Uses spaCy/scispaCy when "
            "available, falls back to regex-based extraction for common "
            "patterns (dates, DOIs, percentages, organizations, methods, "
            "metrics). Returns a structured entity list with frequencies."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to extract entities from (provide text or file_path)",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file to extract entities from (alternative to text)",
                },
                "entity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Entity types to extract (default: all). Options: "
                        "DATE, DOI, PERCENTAGE, ORGANIZATION, METHOD, METRIC, "
                        "CHEMICAL, DISEASE"
                    ),
                },
            },
            "required": [],
        }

    async def execute(
        self,
        text: str = "",
        file_path: str = "",
        entity_types: list[str] | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Extract named entities from text or file."""
        if (err := _require_numpy()) is not None:
            return err
        if not text and file_path:
            workspace = Path(self._workspace_dir)
            full_path = Path(file_path) if Path(file_path).is_absolute() else workspace / file_path
            if not full_path.exists():
                return ToolResult(success=False, error=f"File not found: {full_path}")
            text = _read_text_file(full_path)

        if not text or not text.strip():
            return ToolResult(success=False, error="No text provided. Supply 'text' or 'file_path'.")

        target_types = [t.upper() for t in entity_types] if entity_types else list(self._PATTERNS.keys())
        entities: list[dict[str, Any]] = []
        extraction_method = "regex"

        # Try scispaCy first
        if _HAS_SCISPACY and _HAS_SPACY:
            try:
                nlp = spacy.load("en_core_sci_sm")
                doc = nlp(text[:100000])  # Cap input length for spacy
                extraction_method = "scispacy (en_core_sci_sm)"
                for ent in doc.ents:
                    entity_type = self._map_scispacy_label(ent.label_)
                    if entity_type in target_types:
                        entities.append(
                            {
                                "text": ent.text,
                                "type": entity_type,
                                "start": ent.start_char,
                                "end": ent.end_char,
                            }
                        )
                # Also run regex for patterns spaCy misses
                entities.extend(self._extract_with_regex(text, target_types))
            except OSError:
                entities = self._extract_with_regex(text, target_types)
        elif _HAS_SPACY:
            try:
                nlp = spacy.load("en_core_web_sm")
                doc = nlp(text[:100000])
                extraction_method = "spacy (en_core_web_sm)"
                spacy_type_map = {
                    "ORG": "ORGANIZATION",
                    "DATE": "DATE",
                    "PERCENT": "PERCENTAGE",
                    "GPE": "ORGANIZATION",
                }
                for ent in doc.ents:
                    mapped = spacy_type_map.get(ent.label_, ent.label_)
                    if mapped in target_types:
                        entities.append(
                            {
                                "text": ent.text,
                                "type": mapped,
                                "start": ent.start_char,
                                "end": ent.end_char,
                            }
                        )
                # Supplement with regex for scientific patterns
                entities.extend(self._extract_with_regex(text, target_types))
            except OSError:
                entities = self._extract_with_regex(text, target_types)
        else:
            entities = self._extract_with_regex(text, target_types)

        # Deduplicate and compute frequencies
        entity_counter: Counter[tuple[str, str]] = Counter()
        for ent in entities:
            entity_counter[(ent["text"], ent["type"])] += 1

        seen: set[tuple[str, str]] = set()
        unique_entities: list[dict[str, Any]] = []
        for ent in entities:
            key = (ent["text"], ent["type"])
            if key not in seen:
                seen.add(key)
                ent["frequency"] = entity_counter[key]
                unique_entities.append(ent)

        unique_entities.sort(key=lambda x: x["frequency"], reverse=True)

        result = {
            "extraction_method": extraction_method,
            "total_entities": len(unique_entities),
            "entity_type_counts": dict(Counter(e["type"] for e in unique_entities)),
            "entities": unique_entities[:100],
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))

    @staticmethod
    def _map_scispacy_label(label: str) -> str:
        """Map scispaCy entity labels to standard types."""
        mapping = {
            "CHEBI": "CHEMICAL",
            "CHEMICAL": "CHEMICAL",
            "SIMPLE_CHEMICAL": "CHEMICAL",
            "DISEASE": "DISEASE",
            "DISORDER": "DISEASE",
            "GENE_OR_GENE_PRODUCT": "METHOD",
            "GGP": "METHOD",
            "PROTEIN": "METHOD",
            "ORGANISM": "ORGANIZATION",
            "TAXON": "ORGANIZATION",
        }
        return mapping.get(label.upper(), label.upper())

    def _extract_with_regex(self, text: str, target_types: list[str]) -> list[dict[str, Any]]:
        """Extract entities using regex patterns."""
        entities: list[dict[str, Any]] = []
        for entity_type, pattern in self._PATTERNS.items():
            if entity_type not in target_types:
                continue
            for match in pattern.finditer(text):
                matched_text = match.group().strip()
                if len(matched_text) < 2:
                    continue
                entities.append(
                    {
                        "text": matched_text,
                        "type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                    }
                )
        return entities


# ===================================================================
# 5. BuildKnowledgeGraphTool
# ===================================================================


class BuildKnowledgeGraphTool(Tool):
    """Build a knowledge graph from extracted entities and relationships."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "build_knowledge_graph"

    @property
    def description(self) -> str:
        return (
            "Build a knowledge graph from papers, notes, or all sources. "
            "Nodes include papers, authors, concepts, methods, and datasets. "
            "Edges include cites, authored_by, uses_method, and analyzes_dataset. "
            "Uses NetworkX. Saves as GraphML and JSON."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "enum": ["papers", "notes", "all"],
                    "description": "Source type to build graph from (default: all)",
                },
                "output_path": {
                    "type": "string",
                    "description": "Output directory for graph data (default: knowledge/graph)",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        source: str = "all",
        output_path: str = "knowledge/graph",
        **kwargs: Any,
    ) -> ToolResult:
        """Build knowledge graph from papers and notes."""
        if (err := _require_numpy()) is not None:
            return err
        if not _HAS_NETWORKX:
            return ToolResult(
                success=False,
                error="Package networkx not installed. Run: pip install networkx",
            )

        workspace = Path(self._workspace_dir)
        output_dir = workspace / output_path
        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect source files
        source_files: list[Path] = []
        if source in ("papers", "all"):
            papers_dir = workspace / "literature" / "papers"
            if papers_dir.exists():
                source_files.extend(papers_dir.glob("*.pdf"))
                source_files.extend(papers_dir.glob("*.txt"))
                source_files.extend(papers_dir.glob("*.md"))
        if source in ("notes", "all"):
            notes_dir = workspace / "notes"
            if notes_dir.exists():
                source_files.extend(notes_dir.glob("*.md"))
                source_files.extend(notes_dir.glob("*.txt"))

        if not source_files:
            return ToolResult(
                success=False,
                error=f"No source files found for source='{source}'. Add papers or notes first.",
            )

        # Read texts
        texts: list[tuple[str, str]] = []  # (filename, text)
        for fp in source_files:
            text = _read_text_file(fp)
            if text.strip():
                texts.append((fp.name, text))

        if not texts:
            return ToolResult(success=False, error="No readable text found in source files")

        G = nx.Graph()

        # Entity extraction patterns
        method_pattern = re.compile(
            r"\b(?:regression|ANOVA|SEM|OLS|GMM|VAR|VECM|panel data|"
            r"difference-in-differences|instrumental variable|"
            r"machine learning|deep learning|neural network|"
            r"meta-analysis|systematic review|RCT|logistic regression|"
            r"Bayesian|Monte Carlo|bootstrap|propensity score)\b",
            re.IGNORECASE,
        )
        concept_pattern = re.compile(
            r"\b(?:economic growth|human development|inequality|"
            r"poverty|education|health|infrastructure|trade|"
            r"fiscal policy|monetary policy|labor market|"
            r"sustainable development|urbanization|migration|"
            r"inflation|unemployment|GDP|productivity)\b",
            re.IGNORECASE,
        )
        dataset_pattern = re.compile(
            r"\b(?:Susenas|Sakernas|Podes|IFLS|census|survey data|"
            r"panel data|time series|cross-section|longitudinal)\b",
            re.IGNORECASE,
        )
        citation_pattern = re.compile(r"\(([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?),?\s*(\d{4})\)")
        author_pattern = re.compile(
            r"^(?:by\s+)?([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)*(?:\s+[A-Z][a-z]+)+)",
            re.MULTILINE,
        )

        all_entities: dict[str, dict[str, Any]] = {}
        all_citations: dict[str, dict[str, Any]] = {}

        for filename, text in texts:
            # Add document node
            G.add_node(filename, type="paper")

            # Extract methods
            for match in method_pattern.finditer(text):
                entity = match.group().strip().lower()
                if len(entity) < 2:
                    continue
                if entity not in all_entities:
                    all_entities[entity] = {"type": "method", "docs": set(), "count": 0}
                all_entities[entity]["docs"].add(filename)
                all_entities[entity]["count"] += 1
                G.add_node(entity, type="method")
                G.add_edge(filename, entity, relation="uses_method")

            # Extract concepts
            for match in concept_pattern.finditer(text):
                entity = match.group().strip().lower()
                if entity not in all_entities:
                    all_entities[entity] = {"type": "concept", "docs": set(), "count": 0}
                all_entities[entity]["docs"].add(filename)
                all_entities[entity]["count"] += 1
                G.add_node(entity, type="concept")
                G.add_edge(filename, entity, relation="discusses")

            # Extract datasets
            for match in dataset_pattern.finditer(text):
                entity = match.group().strip().lower()
                if entity not in all_entities:
                    all_entities[entity] = {"type": "dataset", "docs": set(), "count": 0}
                all_entities[entity]["docs"].add(filename)
                all_entities[entity]["count"] += 1
                G.add_node(entity, type="dataset")
                G.add_edge(filename, entity, relation="analyzes_dataset")

            # Extract citations
            for match in citation_pattern.finditer(text):
                author = match.group(1)
                year = match.group(2)
                citation_key = f"{author} ({year})"
                if citation_key not in all_citations:
                    all_citations[citation_key] = {"docs": set(), "count": 0}
                all_citations[citation_key]["docs"].add(filename)
                all_citations[citation_key]["count"] += 1
                G.add_node(citation_key, type="author")
                G.add_edge(filename, citation_key, relation="cites")

            # Extract authors from first 500 chars
            for match in author_pattern.finditer(text[:500]):
                author_name = match.group(1).strip()
                if len(author_name) > 5 and len(author_name) < 60:
                    G.add_node(author_name, type="author")
                    G.add_edge(filename, author_name, relation="authored_by")

        # Add co-occurrence edges
        entity_list = list(all_entities.keys())
        for i in range(len(entity_list)):
            for j in range(i + 1, len(entity_list)):
                e1, e2 = entity_list[i], entity_list[j]
                shared = all_entities[e1]["docs"] & all_entities[e2]["docs"]
                if shared:
                    G.add_edge(e1, e2, relation="co-occurs", weight=len(shared))

        # Compute communities
        communities: list[list[str]] = []
        if len(G.nodes) > 2:
            try:
                from networkx.algorithms.community import greedy_modularity_communities

                comms = greedy_modularity_communities(G)
                communities = [list(c)[:10] for c in list(comms)[:10]]
            except Exception:
                pass

        # Centrality
        centrality = nx.degree_centrality(G) if len(G.nodes) > 0 else {}
        top_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:20]

        # Save as GraphML
        try:
            nx.write_graphml(G, str(output_dir / "knowledge_graph.graphml"))
        except Exception:
            pass

        # Save as JSON
        graph_data = nx.node_link_data(G)
        with open(output_dir / "knowledge_graph.json", "w") as f:
            json.dump(graph_data, f, indent=2, default=str)

        result = {
            "source": source,
            "output_path": str(output_dir),
            "statistics": {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "papers": sum(1 for _, d in G.nodes(data=True) if d.get("type") == "paper"),
                "authors": sum(1 for _, d in G.nodes(data=True) if d.get("type") == "author"),
                "concepts": sum(1 for _, d in G.nodes(data=True) if d.get("type") == "concept"),
                "methods": sum(1 for _, d in G.nodes(data=True) if d.get("type") == "method"),
                "datasets": sum(1 for _, d in G.nodes(data=True) if d.get("type") == "dataset"),
                "communities": len(communities),
            },
            "top_entities": [{"entity": name, "centrality": round(score, 4)} for name, score in top_entities],
            "communities_preview": communities[:5],
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))


# ===================================================================
# 6. QueryKnowledgeGraphTool
# ===================================================================


class QueryKnowledgeGraphTool(Tool):
    """Query the knowledge graph for related entities and paths."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "query_knowledge_graph"

    @property
    def description(self) -> str:
        return (
            "Query the knowledge graph. Supports query types: "
            "'neighbors' (find connected entities), 'path' (shortest path "
            "between entities), 'central' (most central entities), "
            "'community' (community detection around an entity)."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["neighbors", "path", "central", "community"],
                    "description": "Type of graph query to perform",
                },
                "entity": {
                    "type": "string",
                    "description": "Entity name to query (for neighbors/path/community)",
                },
                "depth": {
                    "type": "integer",
                    "description": "Traversal depth for neighbors/community (default: 2)",
                },
            },
            "required": ["query_type"],
        }

    async def execute(
        self,
        query_type: str,
        entity: str = "",
        depth: int = 2,
        **kwargs: Any,
    ) -> ToolResult:
        """Query the knowledge graph."""
        if (err := _require_numpy()) is not None:
            return err
        if not _HAS_NETWORKX:
            return ToolResult(
                success=False,
                error="Package networkx not installed. Run: pip install networkx",
            )

        workspace = Path(self._workspace_dir)
        graph_file = workspace / "knowledge" / "graph" / "knowledge_graph.json"

        if not graph_file.exists():
            return ToolResult(
                success=False,
                error=f"Knowledge graph not found at {graph_file}. Run build_knowledge_graph first.",
            )

        with open(graph_file) as f:
            graph_data = json.load(f)

        G = nx.node_link_graph(graph_data)

        if G.number_of_nodes() == 0:
            return ToolResult(
                success=True,
                content=json.dumps({"results": [], "message": "Empty graph"}),
            )

        if query_type == "neighbors":
            return self._query_neighbors(G, entity, depth)
        elif query_type == "path":
            return self._query_path(G, entity)
        elif query_type == "central":
            return self._query_central(G)
        elif query_type == "community":
            return self._query_community(G, entity, depth)
        else:
            return ToolResult(
                success=False,
                error=f"Unknown query_type: {query_type}. Use: neighbors, path, central, community",
            )

    @staticmethod
    def _find_node(G: Any, entity: str) -> str | None:
        """Find a node by exact or fuzzy match."""
        if entity in G.nodes:
            return entity
        entity_lower = entity.lower()
        for node in G.nodes:
            if str(node).lower() == entity_lower:
                return node
        for node in G.nodes:
            if entity_lower in str(node).lower():
                return node
        return None

    def _query_neighbors(self, G: Any, entity: str, depth: int) -> ToolResult:
        """Find neighbors of an entity up to a given depth."""
        if not entity:
            return ToolResult(success=False, error="'entity' parameter required for neighbors query")

        node = self._find_node(G, entity)
        if node is None:
            available = [str(n) for n in list(G.nodes)[:20]]
            return ToolResult(
                success=False,
                error=f"Entity '{entity}' not found. Available: {', '.join(available)}",
            )

        # BFS to depth
        visited: dict[str, int] = {node: 0}
        queue = [node]
        while queue:
            current = queue.pop(0)
            current_depth = visited[current]
            if current_depth >= depth:
                continue
            for neighbor in G.neighbors(current):
                if neighbor not in visited:
                    visited[neighbor] = current_depth + 1
                    queue.append(neighbor)

        neighbors_by_depth: dict[int, list[dict[str, Any]]] = {}
        for n, d in visited.items():
            if n == node:
                continue
            neighbors_by_depth.setdefault(d, []).append(
                {
                    "entity": str(n),
                    "type": G.nodes[n].get("type", "unknown"),
                    "edge_relation": (
                        G.edges[node, n].get("relation", "connected") if G.has_edge(node, n) else "indirect"
                    ),
                }
            )

        result = {
            "query_type": "neighbors",
            "entity": str(node),
            "entity_type": G.nodes[node].get("type", "unknown"),
            "depth": depth,
            "total_neighbors": sum(len(v) for v in neighbors_by_depth.values()),
            "neighbors_by_depth": {str(d): items for d, items in sorted(neighbors_by_depth.items())},
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))

    def _query_path(self, G: Any, entity: str) -> ToolResult:
        """Find shortest path between two entities (comma-separated in entity param)."""
        if not entity or "," not in entity:
            return ToolResult(
                success=False,
                error="For 'path' query, provide two entities separated by comma: 'entity1,entity2'",
            )

        parts = [p.strip() for p in entity.split(",", 1)]
        node1 = self._find_node(G, parts[0])
        node2 = self._find_node(G, parts[1])

        if node1 is None:
            return ToolResult(success=False, error=f"Entity '{parts[0]}' not found in graph")
        if node2 is None:
            return ToolResult(success=False, error=f"Entity '{parts[1]}' not found in graph")

        try:
            path = nx.shortest_path(G, node1, node2)
            path_details = []
            for i, p in enumerate(path):
                detail: dict[str, Any] = {
                    "entity": str(p),
                    "type": G.nodes[p].get("type", "unknown"),
                }
                if i > 0:
                    edge_data = G.edges.get((path[i - 1], p), {})
                    detail["edge_from_previous"] = edge_data.get("relation", "connected")
                path_details.append(detail)

            result = {
                "query_type": "path",
                "from": str(node1),
                "to": str(node2),
                "path_length": len(path) - 1,
                "path": path_details,
            }
            return ToolResult(success=True, content=json.dumps(result, indent=2))
        except nx.NetworkXNoPath:
            return ToolResult(
                success=True,
                content=json.dumps(
                    {
                        "query_type": "path",
                        "from": str(node1),
                        "to": str(node2),
                        "message": "No path exists between these entities",
                    }
                ),
            )

    @staticmethod
    def _query_central(G: Any) -> ToolResult:
        """Find the most central entities in the graph."""
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G) if len(G.nodes) > 2 else {}

        top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:20]
        top_betweenness = sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:20]

        result = {
            "query_type": "central",
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "top_by_degree": [
                {
                    "entity": str(name),
                    "type": G.nodes[name].get("type", "unknown"),
                    "degree_centrality": round(score, 4),
                    "degree": G.degree(name),
                }
                for name, score in top_degree
            ],
            "top_by_betweenness": [
                {
                    "entity": str(name),
                    "type": G.nodes[name].get("type", "unknown"),
                    "betweenness_centrality": round(score, 4),
                }
                for name, score in top_betweenness
            ],
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))

    def _query_community(self, G: Any, entity: str, depth: int) -> ToolResult:
        """Detect communities and find which community an entity belongs to."""
        communities: list[set[str]] = []
        try:
            from networkx.algorithms.community import greedy_modularity_communities

            comms = greedy_modularity_communities(G)
            communities = [set(str(n) for n in c) for c in comms]
        except Exception:
            return ToolResult(
                success=False,
                error="Community detection failed. Graph may be too small or disconnected.",
            )

        if entity:
            node = self._find_node(G, entity)
            if node is None:
                return ToolResult(success=False, error=f"Entity '{entity}' not found in graph")

            target_community: set[str] | None = None
            community_idx = -1
            for i, comm in enumerate(communities):
                if str(node) in comm:
                    target_community = comm
                    community_idx = i
                    break

            if target_community is None:
                return ToolResult(
                    success=True,
                    content=json.dumps(
                        {
                            "query_type": "community",
                            "entity": str(node),
                            "message": "Entity not found in any community",
                        }
                    ),
                )

            result = {
                "query_type": "community",
                "entity": str(node),
                "community_index": community_idx,
                "community_size": len(target_community),
                "community_members": [
                    {
                        "entity": m,
                        "type": G.nodes[m].get("type", "unknown") if m in G.nodes else "unknown",
                    }
                    for m in sorted(target_community)[:30]
                ],
                "total_communities": len(communities),
            }
        else:
            result = {
                "query_type": "community",
                "total_communities": len(communities),
                "communities": [
                    {
                        "index": i,
                        "size": len(c),
                        "members_preview": sorted(c)[:10],
                    }
                    for i, c in enumerate(communities[:10])
                ],
            }

        return ToolResult(success=True, content=json.dumps(result, indent=2))


# ===================================================================
# 7. PaperQATool
# ===================================================================


class PaperQATool(Tool):
    """Answer questions using embedded papers with citation provenance."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "paper_qa"

    @property
    def description(self) -> str:
        return (
            "Answer research questions using embedded papers with citation "
            "provenance. Uses paper-qa if available for high-quality answers, "
            "falls back to TF-IDF retrieval + context assembly. Returns "
            "answer with source citations and confidence score."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Research question to answer",
                },
                "papers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of paper IDs/filenames to search (optional, searches all if omitted)",
                },
                "max_sources": {
                    "type": "integer",
                    "description": "Maximum number of sources to use (default: 3)",
                },
            },
            "required": ["question"],
        }

    async def execute(
        self,
        question: str,
        papers: list[str] | None = None,
        max_sources: int = 3,
        **kwargs: Any,
    ) -> ToolResult:
        """Answer a question using paper-based RAG."""
        if (err := _require_numpy()) is not None:
            return err
        workspace = Path(self._workspace_dir)
        papers_dir = workspace / "literature" / "papers"

        if not papers_dir.exists():
            papers_dir.mkdir(parents=True, exist_ok=True)
            return ToolResult(
                success=False,
                error=f"Paper directory {papers_dir} is empty. Add papers first.",
            )

        # Collect paper files
        all_paper_files = (
            list(papers_dir.glob("*.pdf")) + list(papers_dir.glob("*.txt")) + list(papers_dir.glob("*.md"))
        )

        if papers:
            paper_files = [f for f in all_paper_files if f.name in papers or f.stem in papers]
            if not paper_files:
                paper_files = all_paper_files
        else:
            paper_files = all_paper_files

        if not paper_files:
            return ToolResult(
                success=False,
                error=f"No papers found in {papers_dir}. Add .pdf, .txt, or .md files.",
            )

        # Try paper-qa first
        if _HAS_PAPER_QA:
            try:
                return await self._answer_with_paperqa(question, paper_files, max_sources)
            except Exception:
                pass

        # Fallback: TF-IDF based retrieval
        return self._answer_with_tfidf(question, paper_files, max_sources)

    async def _answer_with_paperqa(self, question: str, paper_files: list[Path], max_sources: int) -> ToolResult:
        """Answer using paper-qa library."""
        docs = Docs()
        for paper_path in paper_files[: max_sources * 3]:
            try:
                await docs.aadd(str(paper_path))
            except Exception:
                continue

        answer = await docs.aquery(question)

        sources: list[dict[str, str]] = []
        if hasattr(answer, "contexts"):
            for ctx in answer.contexts:
                sources.append(
                    {
                        "citation": ctx.citation if hasattr(ctx, "citation") else str(ctx),
                        "text": ctx.text[:300] if hasattr(ctx, "text") else "",
                    }
                )

        result = {
            "answer": answer.answer if hasattr(answer, "answer") else str(answer),
            "confidence": float(answer.score) if hasattr(answer, "score") else 0.0,
            "sources": sources[:max_sources],
            "method": "paper-qa",
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))

    def _answer_with_tfidf(self, question: str, paper_files: list[Path], max_sources: int) -> ToolResult:
        """Answer using TF-IDF retrieval and context assembly."""
        if not _HAS_SKLEARN:
            return ToolResult(
                success=False,
                error="Package scikit-learn not installed. Run: pip install scikit-learn",
            )

        # Read and chunk papers
        documents: list[str] = []
        doc_metadata: list[dict[str, Any]] = []
        for paper_path in paper_files:
            text = _read_text_file(paper_path)
            if not text.strip():
                continue
            sentences = _simple_sentence_split(text)
            # Group sentences into ~256-token chunks
            chunk_sentences: list[str] = []
            chunk_tokens = 0
            for sent in sentences:
                st = _estimate_tokens(sent)
                if chunk_tokens + st > 256 and chunk_sentences:
                    chunk_text = " ".join(chunk_sentences)
                    documents.append(chunk_text)
                    doc_metadata.append(
                        {
                            "filename": paper_path.name,
                            "path": str(paper_path),
                        }
                    )
                    chunk_sentences = []
                    chunk_tokens = 0
                chunk_sentences.append(sent)
                chunk_tokens += st
            if chunk_sentences:
                chunk_text = " ".join(chunk_sentences)
                documents.append(chunk_text)
                doc_metadata.append(
                    {
                        "filename": paper_path.name,
                        "path": str(paper_path),
                    }
                )

        if not documents:
            return ToolResult(success=False, error="Could not read any papers")

        # TF-IDF vectorization and search
        vectorizer = TfidfVectorizer(max_features=10000, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)
        query_vec = vectorizer.transform([question])
        similarities = sklearn_cosine(query_vec, tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:max_sources]
        sources: list[dict[str, Any]] = []
        context_parts: list[str] = []

        for idx in top_indices:
            if similarities[idx] < 0.01:
                break
            meta = doc_metadata[idx]
            text_snippet = documents[idx][:400]
            sources.append(
                {
                    "filename": meta["filename"],
                    "score": round(float(similarities[idx]), 4),
                    "text_snippet": text_snippet,
                }
            )
            context_parts.append(f"[{meta['filename']}]: {text_snippet}")

        context = "\n\n".join(context_parts)
        confidence = float(np.mean([s["score"] for s in sources])) if sources else 0.0

        result = {
            "answer": f"Based on {len(sources)} retrieved passages:\n\n{context[:2000]}",
            "confidence": round(confidence, 3),
            "sources": sources,
            "method": "tfidf-retrieval",
            "note": (
                "This is a retrieval-only answer. For synthesized answers, install paper-qa: pip install paper-qa"
            ),
        }
        return ToolResult(success=True, content=json.dumps(result, indent=2))
