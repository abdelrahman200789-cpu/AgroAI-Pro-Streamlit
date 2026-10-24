import os
import math
import re
from collections import defaultdict, Counter

class SimpleIRSystem:
    def __init__(self, doc_folder='data/text_docs'):
        self.doc_folder = doc_folder
        self.documents = {}
        self.inverted_index = defaultdict(list)
        self.vocab = set()
        self.doc_vectors = {}
        self.load_documents()
        self.build_inverted_index()
        self.compute_tfidf()

    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def load_documents(self):
        if not os.path.exists(self.doc_folder):
            os.makedirs(self.doc_folder)
        for filename in os.listdir(self.doc_folder):
            if filename.endswith('.txt'):
                path = os.path.join(self.doc_folder, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    self.documents[filename] = f.read()

    def build_inverted_index(self):
        for doc_id, text in self.documents.items():
            tokens = self.tokenize(text)
            for token in set(tokens):
                self.inverted_index[token].append(doc_id)
                self.vocab.add(token)

    def compute_tfidf(self):
        N = len(self.documents)
        if N == 0:
            return

        # 1. IDF Calculation
        idf = {}
        for term in self.vocab:
            df = len(self.inverted_index[term])
            idf[term] = math.log((N + 1) / (df + 1)) + 1

        # 2. TF-IDF Vectors for Documents
        for doc_id, text in self.documents.items():
            tokens = self.tokenize(text)
            tf = Counter(tokens)
            doc_len = len(tokens)
            vector = {}
            for term, count in tf.items():
                norm_tf = count / doc_len
                vector[term] = norm_tf * idf[term]
            self.doc_vectors[doc_id] = vector

    def search(self, query):
        query_tokens = self.tokenize(query)
        if not query_tokens or not self.doc_vectors:
            return []

        # Vector representation for Query
        N = len(self.documents)
        tf = Counter(query_tokens)
        q_len = len(query_tokens)
        q_vector = {}

        for term, count in tf.items():
            df = len(self.inverted_index.get(term, []))
            idf = math.log((N + 1) / (df + 1)) + 1 if df > 0 else 0
            q_vector[term] = (count / q_len) * idf

        # Cosine Similarity Calculation
        scores = {}
        for doc_id, doc_vec in self.doc_vectors.items():
            dot_product = sum(q_vector.get(term, 0) * doc_vec.get(term, 0) for term in q_vector)
            q_norm = math.sqrt(sum(v**2 for v in q_vector.values()))
            doc_norm = math.sqrt(sum(v**2 for v in doc_vec.values()))

            similarity = dot_product / (q_norm * doc_norm) if (q_norm * doc_norm) > 0 else 0
            if similarity > 0:
                scores[doc_id] = similarity

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(doc_id, self.documents[doc_id], score) for doc_id, score in ranked]