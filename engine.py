"""Marginalia engine: PDF reading, passage ranking (BM25) and Ollama calls.

Nothing in this file imports Streamlit, so it can be tested on its own.
"""
from __future__ import annotations

import html
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterator

import pymupdf
import requests

OLLAMA_BASE = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2:latest"

STOP_WORDS = {
    "a", "about", "after", "all", "also", "an", "and", "are", "as", "at", "be",
    "been", "before", "being", "but", "by", "can", "did", "do", "does", "for",
    "from", "had", "has", "have", "he", "her", "his", "how", "i", "if", "in",
    "into", "is", "it", "its", "me", "more", "most", "my", "no", "not", "of",
    "on", "or", "our", "she", "so", "some", "than", "that", "the", "their", "them",
    "there", "these", "they", "this", "to", "too", "was", "we", "were", "what", "when",
    "where", "which", "who", "will", "with", "would", "you", "your",
}


@dataclass
class Passage:
    page: int
    text: str
    terms: Counter
    length: int


@dataclass
class Library:
    """A PDF that has been read and indexed."""
    name: str
    pages: int
    words: int
    passages: list[Passage]
    doc_freq: Counter
    avg_len: float


def _stem(word: str) -> str:
    """Very light stemming so "finish" also matches "finished" and "finishing"."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return [_stem(w) for w in words if w not in STOP_WORDS and len(w) > 2]


def build_library(name: str, pdf_bytes: bytes, chunk_words: int = 180, overlap: int = 35) -> Library:
    """Read a PDF and split each page into overlapping passages.

    Raises ValueError with a plain-language message when the file cannot be used.
    """
    try:
        document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as error:  # PyMuPDF raises several error types for bad files
        raise ValueError(f"This file could not be opened as a PDF ({error}).") from error

    passages: list[Passage] = []
    total_words = 0
    with document:
        if document.needs_pass:
            raise ValueError("This PDF is password protected. Remove the password and upload it again.")
        page_count = document.page_count
        for page_number, page in enumerate(document, start=1):
            words = " ".join(page.get_text("text").split()).split()
            total_words += len(words)
            start = 0
            while start < len(words):
                end = min(start + chunk_words, len(words))
                text = " ".join(words[start:end])
                tokens = tokenize(text)
                passages.append(Passage(page_number, text, Counter(tokens), len(tokens)))
                if end == len(words):
                    break
                start = end - overlap

    if not passages:
        raise ValueError(
            "No selectable text was found. This looks like a scanned PDF. "
            "Run OCR on it first, then upload the searchable version."
        )

    doc_freq: Counter = Counter()
    for passage in passages:
        doc_freq.update(passage.terms.keys())
    avg_len = sum(p.length for p in passages) / len(passages)
    return Library(name, page_count, total_words, passages, doc_freq, avg_len)


def search(library: Library, question: str, limit: int = 5) -> tuple[list[Passage], list[str], bool]:
    """Rank passages with BM25.

    Returns (passages, query_terms, matched). When nothing matches (for example
    "summarize this document"), passages are sampled evenly across the PDF and
    matched is False.
    """
    query_terms = list(dict.fromkeys(tokenize(question)))
    n = len(library.passages)
    k1, b = 1.5, 0.75
    scored: list[tuple[float, int, Passage]] = []
    for position, passage in enumerate(library.passages):
        score = 0.0
        for term in query_terms:
            frequency = passage.terms.get(term, 0)
            if not frequency:
                continue
            df = library.doc_freq[term]
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            norm = frequency + k1 * (1 - b + b * passage.length / max(library.avg_len, 1))
            score += idf * frequency * (k1 + 1) / norm
        if score > 0:
            scored.append((score, position, passage))

    if scored:
        scored.sort(key=lambda item: item[0], reverse=True)
        return [p for _, _, p in scored[:limit]], query_terms, True

    step = max(1, n // limit)
    return library.passages[::step][:limit], query_terms, False


def build_prompt(question: str, passages: list[Passage]) -> str:
    ordered = sorted(passages, key=lambda p: p.page)
    context = "\n\n".join(f"[Page {p.page}] {p.text}" for p in ordered)
    return f"""You answer questions about a PDF using only the supplied excerpts.
If the excerpts do not contain the answer, say exactly that the PDF does not provide enough information.
Do not invent names, dates, numbers, or details that are not in the excerpts.
Include every directly relevant fact from the excerpts.
Cite the page after each claim, like (Page 3). Answer in a short paragraph or bullets.

PDF EXCERPTS:
{context}

QUESTION:
{question}

ANSWER:"""


def stream_answer(prompt: str, model: str, temperature: float = 0.1) -> Iterator[str]:
    """Yield the answer from Ollama piece by piece."""
    with requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={"model": model, "prompt": prompt, "stream": True, "options": {"temperature": temperature}},
        stream=True,
        timeout=(5, 300),
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if data.get("error"):
                raise RuntimeError(data["error"])
            piece = data.get("response", "")
            if piece:
                yield piece
            if data.get("done"):
                break


def installed_models() -> list[str] | None:
    """Names of models installed in Ollama, or None when Ollama is not running."""
    try:
        response = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=1.5)
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]
    except (requests.RequestException, ValueError):
        return None


def snippet(text: str, terms: list[str], width: int = 340) -> str:
    """Trim a passage to a window around the first matching term."""
    if len(text) <= width:
        return text
    lowered = text.lower()
    hits = [lowered.find(t) for t in terms if lowered.find(t) >= 0]
    start = max(0, min(hits) - 90) if hits else 0
    piece = text[start:start + width].strip()
    return ("…" if start > 0 else "") + piece + ("…" if start + width < len(text) else "")


def mark_terms(text: str, terms: list[str]) -> str:
    """HTML-escape text and wrap query terms in <mark> (the highlighter effect)."""
    safe = html.escape(text)
    words = [re.escape(t) for t in sorted(terms, key=len, reverse=True) if "'" not in t]
    if not words:
        return safe
    return re.sub(r"\b((?:" + "|".join(words) + r")\w*)", r"<mark>\1</mark>", safe, flags=re.I)
