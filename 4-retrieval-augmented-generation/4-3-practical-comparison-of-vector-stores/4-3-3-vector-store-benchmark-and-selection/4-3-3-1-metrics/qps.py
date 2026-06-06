import time

import faiss
import numpy as np
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


def build_documents(rows_count: int) -> pd.DataFrame:
    """Build sample documents for a vector search benchmark.
    Args:
        rows_count (int): Number of sample documents."""
    document_ids = [f'doc_{index}' for index in range(rows_count)]
    texts = [f'sample document text {index}' for index in range(rows_count)]

    data = pd.DataFrame(
        {
            'document_id': document_ids,
            'text': texts,
        }
    )
    return data


def create_vectors(data: pd.DataFrame, vector_size: int) -> pd.DataFrame:
    """Create sample vectors for documents.
    Args:
        data (pd.DataFrame): DataFrame with documents.
        vector_size (int): Size of each vector."""
    random_vectors = np.random.random(
        (len(data), vector_size)
    ).astype('float32')

    vector_data = data.copy()
    vector_data['vector'] = random_vectors.tolist()
    return vector_data


def build_queries(
    queries_count: int,
    vector_size: int,
) -> np.ndarray:
    """Build sample query vectors.
    Args:
        queries_count (int): Number of query vectors.
        vector_size (int): Size of each query vector."""
    query_vectors = np.random.random(
        (queries_count, vector_size)
    ).astype('float32')
    return query_vectors


def build_faiss(data: pd.DataFrame, vector_size: int) -> faiss.IndexFlatL2:
    """Build FAISS index with document vectors.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector."""
    vectors = np.array(data['vector'].to_list()).astype('float32')

    index = faiss.IndexFlatL2(vector_size)
    index.add(vectors)

    return index


def build_qdrant(
    data: pd.DataFrame,
    vector_size: int,
    collection_name: str,
) -> QdrantClient:
    """Build Qdrant collection with document vectors.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector.
        collection_name (str): Name of Qdrant collection."""
    client = QdrantClient(location=':memory:')

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    points = [
        PointStruct(
            id=index,
            vector=row['vector'],
            payload={
                'document_id': row['document_id'],
                'text': row['text'],
            },
        )
        for index, row in data.reset_index(drop=True).iterrows()
    ]

    client.upsert(
        collection_name=collection_name,
        points=points,
    )

    return client


def search_faiss(
    index: faiss.IndexFlatL2,
    query_vector: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Search nearest vectors in FAISS.
    Args:
        index (faiss.IndexFlatL2): FAISS index with document vectors.
        query_vector (np.ndarray): Single query vector.
        top_k (int): Number of nearest vectors."""
    distances, indices = index.search(query_vector, top_k)
    return distances, indices


def search_qdrant(
    client: QdrantClient,
    collection_name: str,
    query_vector: np.ndarray,
    top_k: int,
) -> object:
    """Search nearest vectors in Qdrant.
    Args:
        client (QdrantClient): Qdrant client with indexed vectors.
        collection_name (str): Name of Qdrant collection.
        query_vector (np.ndarray): Single query vector.
        top_k (int): Number of nearest vectors."""
    search_result = client.query_points(
        collection_name=collection_name,
        query=query_vector.reshape(-1).tolist(),
        limit=top_k,
    )
    return search_result


def measure_faiss(
    index: faiss.IndexFlatL2,
    query_vectors: np.ndarray,
    top_k: int,
) -> pd.DataFrame:
    """Measure FAISS queries per second.
    Args:
        index (faiss.IndexFlatL2): FAISS index with document vectors.
        query_vectors (np.ndarray): Query vectors for benchmark.
        top_k (int): Number of nearest vectors."""
    started_at = time.perf_counter()

    for query_vector in query_vectors:
        query_batch = query_vector.reshape(1, -1)
        search_faiss(
            index=index,
            query_vector=query_batch,
            top_k=top_k,
        )

    finished_at = time.perf_counter()
    elapsed_seconds = finished_at - started_at
    queries_count = len(query_vectors)

    metric_data = pd.DataFrame(
        [
            {
                'storage_name': 'faiss',
                'queries_count': queries_count,
                'elapsed_seconds': round(elapsed_seconds, 6),
                'qps': round(queries_count / elapsed_seconds, 2),
            }
        ]
    )
    return metric_data


def measure_qdrant(
    client: QdrantClient,
    collection_name: str,
    query_vectors: np.ndarray,
    top_k: int,
) -> pd.DataFrame:
    """Measure Qdrant queries per second.
    Args:
        client (QdrantClient): Qdrant client with indexed vectors.
        collection_name (str): Name of Qdrant collection.
        query_vectors (np.ndarray): Query vectors for benchmark.
        top_k (int): Number of nearest vectors."""
    started_at = time.perf_counter()

    for query_vector in query_vectors:
        query_batch = query_vector.reshape(1, -1)
        search_qdrant(
            client=client,
            collection_name=collection_name,
            query_vector=query_batch,
            top_k=top_k,
        )

    finished_at = time.perf_counter()
    elapsed_seconds = finished_at - started_at
    queries_count = len(query_vectors)

    metric_data = pd.DataFrame(
        [
            {
                'storage_name': 'qdrant',
                'queries_count': queries_count,
                'elapsed_seconds': round(elapsed_seconds, 6),
                'qps': round(queries_count / elapsed_seconds, 2),
            }
        ]
    )
    return metric_data


def run_benchmark(
    data: pd.DataFrame,
    query_vectors: np.ndarray,
    vector_size: int,
    top_k: int,
) -> pd.DataFrame:
    """Run QPS benchmark.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        query_vectors (np.ndarray): Query vectors for benchmark.
        vector_size (int): Size of each vector.
        top_k (int): Number of nearest vectors."""
    collection_name = 'qps_benchmark'

    faiss_index = build_faiss(
        data=data,
        vector_size=vector_size,
    )
    qdrant_client = build_qdrant(
        data=data,
        vector_size=vector_size,
        collection_name=collection_name,
    )

    faiss_metric_data = measure_faiss(
        index=faiss_index,
        query_vectors=query_vectors,
        top_k=top_k,
    )
    qdrant_metric_data = measure_qdrant(
        client=qdrant_client,
        collection_name=collection_name,
        query_vectors=query_vectors,
        top_k=top_k,
    )

    benchmark_results = pd.concat(
        [faiss_metric_data, qdrant_metric_data],
        ignore_index=True,
    )
    return benchmark_results


if __name__ == '__main__':
    embedding_size = 384
    search_top_k = 5

    documents_data = build_documents(rows_count=1000)
    vectors_data = create_vectors(
        data=documents_data,
        vector_size=embedding_size,
    )
    query_vectors_data = build_queries(
        queries_count=1000,
        vector_size=embedding_size,
    )

    qps_results = run_benchmark(
        data=vectors_data,
        query_vectors=query_vectors_data,
        vector_size=embedding_size,
        top_k=search_top_k,
    )

    print('QPS benchmark results:')
    print(qps_results.to_string(index=False))
