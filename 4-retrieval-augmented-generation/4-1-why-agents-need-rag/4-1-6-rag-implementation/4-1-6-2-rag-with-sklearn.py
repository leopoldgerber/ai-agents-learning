from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Knowledge source
knowledge_base = """
Machine learning is a branch of artificial intelligence.
Neural networks are used for pattern recognition.
Deep learning is a subset of machine learning.
Supervised learning algorithms require labeled data.
Clustering is an unsupervised learning method.
"""

# Split into fragments
fragments = [s.strip() for s in knowledge_base.split('.') if s.strip()]

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()
fragment_vectors = vectorizer.fit_transform(fragments)


def rag_with_sklearn(query, top_k=2):
    """RAG using sklearn."""
    # Vectorize the query
    query_vector = vectorizer.transform([query])

    # Compute cosine similarity
    similarities = cosine_similarity(query_vector, fragment_vectors)[0]

    # Get indices of top-k results
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0:
            results.append({
                'fragment': fragments[idx],
                'similarity': similarities[idx]
            })

    return results


# Usage example
query = 'Tell me about neural networks'
results = rag_with_sklearn(query, top_k=2)

print(f'Query: {query}\n')
for i, result in enumerate(results, 1):
    print(f"Result {i} (relevance: {result['similarity']:.3f}):")
    print(f"{result['fragment']}\n")
