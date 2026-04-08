import numpy as np
from collections import Counter
import re


# Knowledge source
knowledge_base = """
Machine learning is a branch of artificial intelligence.
Neural networks are used for pattern recognition.
Deep learning is a subset of machine learning.
Supervised learning algorithms require labeled data.
Clustering is an unsupervised learning method.
"""


# Split into fragments
def split_text(text):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    return sentences


fragments = split_text(knowledge_base)


# Simple vectorization based on TF-IDF (manual implementation)
def create_vocabulary(texts):
    """Create a vocabulary of all unique words."""
    all_words = []
    for text in texts:
        words = re.findall(r'\w+', text.lower())
        all_words.extend(words)
    return sorted(set(all_words))


def text_to_vector(text, vocabulary):
    """Convert text into a vector based on word frequency."""
    words = re.findall(r'\w+', text.lower())
    word_count = Counter(words)

    vector = []
    for word in vocabulary:
        vector.append(word_count.get(word, 0))

    return np.array(vector, dtype=float)


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot_product / (norm1 * norm2)


# Prepare data
vocabulary = create_vocabulary(fragments)
fragment_vectors = [text_to_vector(frag, vocabulary) for frag in fragments]


# RAG function
def simple_rag(query, top_k=2):
    """Find the most relevant fragments."""
    query_vector = text_to_vector(query, vocabulary)

    # Compute similarity with each fragment
    similarities = []
    for i, frag_vec in enumerate(fragment_vectors):
        sim = cosine_similarity(query_vector, frag_vec)
        similarities.append((i, sim))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top-k fragments
    results = []
    for i, sim in similarities[:top_k]:
        if sim > 0:
            results.append({
                'fragment': fragments[i],
                'similarity': sim
            })

    return results


# Example usage
query = 'What is deep learning?'
results = simple_rag(query, top_k=2)

print(f'Query: {query}\n')
for i, result in enumerate(results, 1):
    print(f"Result {i} (similarity: {result['similarity']:.3f}):")
    print(f"{result['fragment']}\n")
