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


def build_flat(
    vectors: np.ndarray,
    dimension: int,
) -> faiss.IndexFlatL2:
    """Build exact IndexFlatL2 index.
    Args:
        vectors (np.ndarray): Database vectors.
        dimension (int): Vector dimension."""
    index_flat = faiss.IndexFlatL2(dimension)
    index_flat.add(vectors)

    return index_flat


def build_ivfpq(
    vectors: np.ndarray,
    dimension: int,
    cluster_count: int,
    subspace_count: int,
    bits_count: int,
) -> faiss.IndexIVFPQ:
    """Build trained IVF-PQ index.
    Args:
        vectors (np.ndarray): Database vectors.
        dimension (int): Vector dimension.
        cluster_count (int): Number of IVF clusters.
        subspace_count (int): Number of PQ subspaces.
        bits_count (int): Bits per PQ subspace."""
    quantizer = faiss.IndexFlatL2(dimension)
    index_ivfpq = faiss.IndexIVFPQ(
        quantizer,
        dimension,
        cluster_count,
        subspace_count,
        bits_count,
    )

    index_ivfpq.train(vectors)
    index_ivfpq.add(vectors)

    return index_ivfpq


def search_index(
    index: Any,
    queries: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Search nearest neighbors in FAISS index.
    Args:
        index (Any): FAISS index for search.
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


def estimate_memory(
    num_vectors: int,
    dimension: int,
    subspace_count: int,
    bits_count: int,
) -> dict[str, float]:
    """Estimate original and compressed vector memory.
    Args:
        num_vectors (int): Number of vectors.
        dimension (int): Vector dimension.
        subspace_count (int): Number of PQ subspaces.
        bits_count (int): Bits per PQ subspace."""
    original_bytes = num_vectors * dimension * 4
    compressed_bytes = num_vectors * subspace_count * (bits_count // 8)

    memory_stats = {
        'original_mb': round(original_bytes / (1024**2), 2),
        'compressed_mb': round(compressed_bytes / (1024**2), 2),
        'compression_ratio': round(original_bytes / compressed_bytes, 2),
    }
    return memory_stats


def build_metrics(
    recall_value: float,
    search_time_ms: float,
    memory_stats: dict[str, float],
) -> dict[str, float]:
    """Build IVF-PQ metrics.
    Args:
        recall_value (float): Recall score.
        search_time_ms (float): Search time in milliseconds.
        memory_stats (dict[str, float]): Memory comparison values."""
    metrics = {
        'recall_at_k': round(recall_value, 4),
        'search_time_ms': round(search_time_ms, 4),
        'original_mb': memory_stats['original_mb'],
        'compressed_mb': memory_stats['compressed_mb'],
        'compression_ratio': memory_stats['compression_ratio'],
    }
    return metrics


def print_metrics(metrics: dict[str, float]) -> dict[str, float]:
    """Print IVF-PQ metrics.
    Args:
        metrics (dict[str, float]): IVF-PQ metrics."""
    for key, value in metrics.items():
        print(f'{key}: {value}')

    return metrics


if __name__ == '__main__':
    vectors, queries = generate_vectors(
        num_vectors=100_000,
        dimension=128,
        num_queries=100,
    )

    flat_index = build_flat(
        vectors=vectors,
        dimension=128,
    )
    true_distances, true_indices, flat_time_ms = search_index(
        index=flat_index,
        queries=queries,
        top_k=10,
    )

    ivfpq_index = build_ivfpq(
        vectors=vectors,
        dimension=128,
        cluster_count=100,
        subspace_count=16,
        bits_count=8,
    )
    ivfpq_index.nprobe = 10

    found_distances, found_indices, search_time_ms = search_index(
        index=ivfpq_index,
        queries=queries,
        top_k=10,
    )

    recall_value = compute_recall(
        true_indices=true_indices,
        found_indices=found_indices,
        top_k=10,
    )
    memory_stats = estimate_memory(
        num_vectors=100_000,
        dimension=128,
        subspace_count=16,
        bits_count=8,
    )
    metrics = build_metrics(
        recall_value=recall_value,
        search_time_ms=search_time_ms,
        memory_stats=memory_stats,
    )
    printed_metrics = print_metrics(metrics=metrics)
