import math
import re
from collections import Counter, defaultdict
from pathlib import Path


class SimpleIRSystem:
    """Small TF-IDF information-retrieval engine for local agriculture notes."""

    def __init__(self, doc_folder="data/text_docs"):
        self.doc_folder = Path(doc_folder)
        if not self.doc_folder.is_absolute():
            self.doc_folder = Path(__file__).resolve().parent / self.doc_folder
        self.documents = {}
        self.inverted_index = defaultdict(list)
        self.vocab = set()
        self.doc_vectors = {}
        self.load_documents()
        self.build_inverted_index()
        self.compute_tfidf()

    @staticmethod
    def tokenize(text):
        return re.findall(r"\b[a-zA-Z0-9]+\b", str(text).lower())

    def load_documents(self):
        self.doc_folder.mkdir(parents=True, exist_ok=True)
        self.documents = {}
        for path in sorted(self.doc_folder.glob("*.txt")):
            self.documents[path.name] = path.read_text(encoding="utf-8")

    def rebuild(self):
        self.inverted_index.clear()
        self.vocab.clear()
        self.doc_vectors.clear()
        self.load_documents()
        self.build_inverted_index()
        self.compute_tfidf()

    def build_inverted_index(self):
        for doc_id, text in self.documents.items():
            for token in set(self.tokenize(text)):
                self.inverted_index[token].append(doc_id)
                self.vocab.add(token)

    def compute_tfidf(self):
        n_docs = len(self.documents)
        if not n_docs:
            return
        idf = {
            term: math.log((n_docs + 1) / (len(self.inverted_index[term]) + 1)) + 1
            for term in self.vocab
        }
        for doc_id, text in self.documents.items():
            tokens = self.tokenize(text)
            if not tokens:
                self.doc_vectors[doc_id] = {}
                continue
            counts = Counter(tokens)
            self.doc_vectors[doc_id] = {
                term: (count / len(tokens)) * idf[term]
                for term, count in counts.items()
            }

    @staticmethod
    def _cosine(a, b):
        dot = sum(value * b.get(term, 0.0) for term, value in a.items())
        norm_a = math.sqrt(sum(value * value for value in a.values()))
        norm_b = math.sqrt(sum(value * value for value in b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def search(self, query, limit=5):
        tokens = self.tokenize(query)
        if not tokens or not self.doc_vectors:
            return []
        counts = Counter(tokens)
        n_docs = len(self.documents)
        q_vector = {}
        for term, count in counts.items():
            df = len(self.inverted_index.get(term, []))
            if df:
                idf = math.log((n_docs + 1) / (df + 1)) + 1
                q_vector[term] = (count / len(tokens)) * idf
        if not q_vector:
            return []
        ranked = []
        for doc_id, vector in self.doc_vectors.items():
            score = self._cosine(q_vector, vector)
            if score > 0:
                ranked.append((doc_id, self.documents[doc_id], score))
        return sorted(ranked, key=lambda item: item[2], reverse=True)[:limit]
