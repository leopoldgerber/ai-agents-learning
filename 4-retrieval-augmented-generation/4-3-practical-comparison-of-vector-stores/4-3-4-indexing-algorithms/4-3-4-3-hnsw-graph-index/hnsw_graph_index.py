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


def build_hnsw(
    vectors: np.ndarray,
    dimension: int,
    links_count: int,
    construction_value: int,
) -> faiss.IndexHNSWFlat:
    """Build HNSW graph index.
    Args:
        vectors (np.ndarray): Database vectors.
        dimension (int): Vector dimension.
        links_count (int): Number of graph links per node.
        construction_value (int): Graph construction quality."""
    index_hnsw = faiss.IndexHNSWFlat(dimension, links_count)
    index_hnsw.hnsw.efConstruction = construction_value
    index_hnsw.add(vectors)

    return index_hnsw


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


def test_ef_search(
    index_hnsw: faiss.IndexHNSWFlat,
    queries: np.ndarray,
    true_indices: np.ndarray,
    top_k: int,
    ef_values: list[int],
) -> list[dict[str, float]]:
    """Test HNSW with different efSearch values.
    Args:
        index_hnsw (faiss.IndexHNSWFlat): Built HNSW index.
        queries (np.ndarray): Query vectors.
        true_indices (np.ndarray): Exact nearest neighbor indices.
        top_k (int): Number of nearest neighbors.
        ef_values (list[int]): Search quality values."""
    results_list = []

    for ef_value in ef_values:
        index_hnsw.hnsw.efSearch = ef_value

        distances, indices, search_time_ms = search_index(
            index=index_hnsw,
            queries=queries,
            top_k=top_k,
        )
        recall_value = compute_recall(
            true_indices=true_indices,
            found_indices=indices,
            top_k=top_k,
        )
        results_list.append(
            {
                'ef_search': float(ef_value),
                'recall_at_k': round(recall_value, 4),
                'search_time_ms': round(search_time_ms, 4),
                'first_distance': float(distances[0][0]),
            },
        )

    return results_list


def print_results(
    results_list: list[dict[str, float]],
) -> list[dict[str, float]]:
    """Print HNSW benchmark results.
    Args:
        results_list (list[dict[str, float]]): HNSW benchmark rows."""
    for result_item in results_list:
        print(
            'efSearch={ef_search:.0f} | recall={recall_at_k:.4f} | '
            'time_ms={search_time_ms:.4f}'.format(**result_item),
        )

    return results_list


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

    hnsw_index = build_hnsw(
        vectors=vectors,
        dimension=128,
        links_count=32,
        construction_value=200,
    )
    results_list = test_ef_search(
        index_hnsw=hnsw_index,
        queries=queries,
        true_indices=true_indices,
        top_k=10,
        ef_values=[16, 32, 64, 128],
    )
    printed_results = print_results(results_list=results_list)
