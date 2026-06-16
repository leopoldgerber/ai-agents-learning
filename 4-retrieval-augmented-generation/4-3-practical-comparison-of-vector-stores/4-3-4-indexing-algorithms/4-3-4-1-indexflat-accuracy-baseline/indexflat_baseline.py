import time
from typing import Any

import faiss
import numpy as np


def generate_vectors(
    num_vectors: int,
    dimension: int,
    num_queries: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate test vectors and query vectors.
    Args:
        num_vectors (int): Number of database vectors.
        dimension (int): Vector dimension.
        num_queries (int): Number of query vectors."""
    rng = np.random.default_rng(seed=42)

    vectors = rng.random(
        size=(num_vectors, dimension),
        dtype=np.float32,
    )
    queries = rng.random(
        size=(num_queries, dimension),
        dtype=np.float32,
    )

    return vectors, queries


def build_index(
    vectors: np.ndarray,
    dimension: int,
) -> faiss.IndexFlatL2:
    """Build exact IndexFlatL2 index.
    Args:
        vectors (np.ndarray): Database vectors.
        dimension (int): Vector dimension."""
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    return index


def search_index(
    index: faiss.IndexFlatL2,
    queries: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Search nearest neighbors in FAISS index.
    Args:
        index (faiss.IndexFlatL2): FAISS index for search.
        queries (np.ndarray): Query vectors.
        top_k (int): Number of nearest neighbors."""
    start_time = time.perf_counter()
    distances, indices = index.search(queries, top_k)
    search_time_ms = (time.perf_counter() - start_time) * 1000

    return distances, indices, search_time_ms


def compute_recall(
    true_indices: np.ndarray,
    found_indices: np.ndarray,
    top_k: int,
) -> float:
    """Compute Recall at k for search results.
    Args:
        true_indices (np.ndarray): Exact nearest neighbor indices.
        found_indices (np.ndarray): Found nearest neighbor indices.
        top_k (int): Number of neighbors for comparison."""
    recall_sum = 0.0

    for row_index in range(len(true_indices)):
        true_set = set(true_indices[row_index, :top_k])
        found_set = set(found_indices[row_index, :top_k])
        recall_sum += len(true_set & found_set) / top_k

    recall_value = recall_sum / len(true_indices)
    return recall_value


def build_metrics(
    distances: np.ndarray,
    indices: np.ndarray,
    search_time_ms: float,
    recall_value: float,
) -> dict[str, Any]:
    """Build output metrics for IndexFlat baseline.
    Args:
        distances (np.ndarray): Search distances.
        indices (np.ndarray): Search result indices.
        search_time_ms (float): Search time in milliseconds.
        recall_value (float): Recall score."""
    metrics = {
        'index_type': 'IndexFlatL2',
        'query_count': len(indices),
        'first_result_id': int(indices[0][0]),
        'first_distance': float(distances[0][0]),
        'search_time_ms': round(search_time_ms, 4),
        'recall_at_k': round(recall_value, 4),
    }
    return metrics


def print_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """Print IndexFlat metrics.
    Args:
        metrics (dict[str, Any]): Metrics for output."""
    for key, value in metrics.items():
        print(f'{key}: {value}')

    return metrics


if __name__ == '__main__':
    vectors, queries = generate_vectors(
        num_vectors=10_000,
        dimension=128,
        num_queries=100,
    )

    exact_index = build_index(
        vectors=vectors,
        dimension=128,
    )

    true_distances, true_indices, search_time_ms = search_index(
        index=exact_index,
        queries=queries,
        top_k=10,
    )

    found_distances, found_indices, found_time_ms = search_index(
        index=exact_index,
        queries=queries,
        top_k=10,
    )

    recall_value = compute_recall(
        true_indices=true_indices,
        found_indices=found_indices,
        top_k=10,
    )

    metrics = build_metrics(
        distances=found_distances,
        indices=found_indices,
        search_time_ms=found_time_ms,
        recall_value=recall_value,
    )

    printed_metrics = print_metrics(metrics=metrics)
