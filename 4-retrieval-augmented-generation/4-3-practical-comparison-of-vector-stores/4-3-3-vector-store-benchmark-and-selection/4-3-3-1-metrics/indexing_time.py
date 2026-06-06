import time

import faiss
import numpy as np
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


def build_documents(rows_count: int) -> pd.DataFrame:
    """Build sample documents for a RAG benchmark.
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


def index_faiss(data: pd.DataFrame, vector_size: int) -> faiss.IndexFlatL2:
    """Index document vectors in FAISS.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector."""
    vectors = np.array(data['vector'].to_list()).astype('float32')
    index = faiss.IndexFlatL2(vector_size)
    index.add(vectors)

    return index


def index_qdrant(
    data: pd.DataFrame,
    vector_size: int,
    collection_name: str,
) -> QdrantClient:
    """Index document vectors in Qdrant.
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


def measure_faiss(
    data: pd.DataFrame,
    vector_size: int,
    batch_name: str,
) -> pd.DataFrame:
    """Measure FAISS indexing time.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector.
        batch_name (str): Name of benchmark batch."""
    started_at = time.perf_counter()
    index = index_faiss(data=data, vector_size=vector_size)
    finished_at = time.perf_counter()

    elapsed_seconds = finished_at - started_at
    vectors_count = index.ntotal

    metric_data = pd.DataFrame(
        [
            {
                'storage_name': 'faiss',
                'batch_name': batch_name,
                'vectors_count': vectors_count,
                'indexing_time_seconds': round(elapsed_seconds, 6),
                'vectors_per_second': round(
                    vectors_count / elapsed_seconds,
                    2,
                ),
            }
        ]
    )
    return metric_data


def measure_qdrant(
    data: pd.DataFrame,
    vector_size: int,
    batch_name: str,
) -> pd.DataFrame:
    """Measure Qdrant indexing time.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector.
        batch_name (str): Name of benchmark batch."""
    collection_name = f'benchmark_{batch_name}'

    started_at = time.perf_counter()
    index_qdrant(
        data=data,
        vector_size=vector_size,
        collection_name=collection_name,
    )
    finished_at = time.perf_counter()

    elapsed_seconds = finished_at - started_at
    vectors_count = len(data)

    metric_data = pd.DataFrame(
        [
            {
                'storage_name': 'qdrant',
                'batch_name': batch_name,
                'vectors_count': vectors_count,
                'indexing_time_seconds': round(elapsed_seconds, 6),
                'vectors_per_second': round(
                    vectors_count / elapsed_seconds,
                    2,
                ),
            }
        ]
    )
    return metric_data


def run_benchmark(data: pd.DataFrame, vector_size: int) -> pd.DataFrame:
    """Run indexing time benchmark.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector."""
    batch_sizes = [100, 500, 1000]
    results_list = []

    for batch_size in batch_sizes:
        batch_data = data.head(batch_size)
        batch_name = f'batch_{batch_size}'

        faiss_metric_data = measure_faiss(
            data=batch_data,
            vector_size=vector_size,
            batch_name=batch_name,
        )
        qdrant_metric_data = measure_qdrant(
            data=batch_data,
            vector_size=vector_size,
            batch_name=batch_name,
        )

        results_list.extend([faiss_metric_data, qdrant_metric_data])

    benchmark_results = pd.concat(results_list, ignore_index=True)
    return benchmark_results


if __name__ == '__main__':
    embedding_size = 384

    documents_data = build_documents(rows_count=1000)
    vectors_data = create_vectors(
        data=documents_data,
        vector_size=embedding_size,
    )

    indexing_time_results = run_benchmark(
        data=vectors_data,
        vector_size=embedding_size,
    )

    print('Indexing time benchmark results:')
    print(indexing_time_results.to_string(index=False))
