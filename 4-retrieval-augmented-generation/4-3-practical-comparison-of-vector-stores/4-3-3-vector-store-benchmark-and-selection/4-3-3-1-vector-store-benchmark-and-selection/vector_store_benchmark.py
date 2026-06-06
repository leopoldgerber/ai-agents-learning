import time
from typing import Any

import faiss
import numpy as np


def generate_vectors(
    num_documents: int,
    dimension: int,
    num_queries: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate normalized test vectors and queries.
    Args:
        num_documents (int): Number of document vectors.
        dimension (int): Vector dimension.
        num_queries (int): Number of query vectors."""
    rng = np.random.default_rng(seed=42)

    vectors = rng.random(
        size=(num_documents, dimension),
        dtype=np.float32,
    )
    vector_norms = np.linalg.norm(
        vectors,
        axis=1,
        keepdims=True,
    )
    vectors = vectors / vector_norms

    query_indices = rng.choice(
        num_documents,
        size=num_queries,
        replace=False,
    )
    queries = vectors[query_indices].copy()
    noise = rng.normal(
        loc=0.0,
        scale=0.1,
        size=queries.shape,
    ).astype('float32')
    queries = queries + noise

    query_norms = np.linalg.norm(
        queries,
        axis=1,
        keepdims=True,
    )
    queries = queries / query_norms

    return vectors, queries


def benchmark_faiss(
    vectors: np.ndarray,
    queries: np.ndarray,
    top_k: int,
) -> dict[str, Any]:
    """Benchmark FAISS indexing and search.
    Args:
        vectors (np.ndarray): Document vectors.
        queries (np.ndarray): Query vectors.
        top_k (int): Number of nearest results."""
    dimension = vectors.shape[1]

    start_time = time.perf_counter()
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    index_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    single_distances, single_indices = index.search(
        queries[:1],
        top_k,
    )
    single_query_ms = (time.perf_counter() - start_time) * 1000

    start_time = time.perf_counter()
    batch_distances, batch_indices = index.search(
        queries,
        top_k,
    )
    batch_time = time.perf_counter() - start_time
    qps_value = len(queries) / batch_time

    memory_mb = vectors.nbytes / (1024 * 1024)

    result = {
        'name': 'FAISS',
        'index_time_sec': round(index_time, 4),
        'single_query_ms': round(single_query_ms, 4),
        'qps': round(qps_value, 2),
        'memory_mb': round(memory_mb, 2),
        'first_result_id': int(single_indices[0][0]),
        'first_distance': float(single_distances[0][0]),
        'batch_shape': batch_indices.shape,
        'distance_shape': batch_distances.shape,
    }
    return result


def choose_store(
    needs_filters: bool,
    needs_schema: bool,
    fits_memory: bool,
    production_mode: bool,
) -> str:
    """Choose vector store from project requirements.
    Args:
        needs_filters (bool): Whether metadata filters are required.
        needs_schema (bool): Whether rich object schema is required.
        fits_memory (bool): Whether the dataset fits into RAM.
        production_mode (bool): Whether production reliability is required."""
    if needs_schema:
        return 'Weaviate'

    if production_mode and needs_filters:
        return 'Qdrant'

    if fits_memory and not needs_filters:
        return 'FAISS'

    if needs_filters:
        return 'Qdrant'

    return 'FAISS'


def print_result(result: dict[str, Any]) -> dict[str, Any]:
    """Print benchmark result.
    Args:
        result (dict[str, Any]): Benchmark metrics."""
    print(f"Store: {result['name']}")
    print(f"Index time: {result['index_time_sec']} sec")
    print(f"Single query: {result['single_query_ms']} ms")
    print(f"QPS: {result['qps']}")
    print(f"Memory: {result['memory_mb']} MB")
    print(f"First result ID: {result['first_result_id']}")

    return result


if __name__ == '__main__':
    vectors, queries = generate_vectors(
        num_documents=10_000,
        dimension=384,
        num_queries=100,
    )
    faiss_result = benchmark_faiss(
        vectors=vectors,
        queries=queries,
        top_k=5,
    )
    printed_result = print_result(result=faiss_result)

    selected_store = choose_store(
        needs_filters=True,
        needs_schema=False,
        fits_memory=False,
        production_mode=True,
    )
    print(f'Selected vector store: {selected_store}')
