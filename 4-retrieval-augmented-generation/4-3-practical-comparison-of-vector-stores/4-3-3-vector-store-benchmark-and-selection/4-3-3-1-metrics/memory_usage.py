import os

import faiss
import numpy as np
import pandas as pd
import psutil
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


def build_documents(rows_count: int) -> pd.DataFrame:
    """Build sample documents for a vector storage benchmark.
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


def get_memory_mb() -> float:
    """Get current process memory usage in megabytes.
    Args:
        None: No arguments."""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    return memory_mb


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


def measure_faiss(
    data: pd.DataFrame,
    vector_size: int,
) -> pd.DataFrame:
    """Measure FAISS memory usage.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector."""
    before_memory_mb = get_memory_mb()
    index = build_faiss(data=data, vector_size=vector_size)
    after_memory_mb = get_memory_mb()

    metric_data = pd.DataFrame(
        [
            {
                'storage_name': 'faiss',
                'vectors_count': index.ntotal,
                'before_memory_mb': round(before_memory_mb, 4),
                'after_memory_mb': round(after_memory_mb, 4),
                'memory_delta_mb': round(
                    after_memory_mb - before_memory_mb,
                    4,
                ),
            }
        ]
    )
    return metric_data


def measure_qdrant(
    data: pd.DataFrame,
    vector_size: int,
) -> pd.DataFrame:
    """Measure Qdrant memory usage.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector."""
    collection_name = 'memory_usage_benchmark'

    before_memory_mb = get_memory_mb()
    build_qdrant(
        data=data,
        vector_size=vector_size,
        collection_name=collection_name,
    )
    after_memory_mb = get_memory_mb()

    metric_data = pd.DataFrame(
        [
            {
                'storage_name': 'qdrant',
                'vectors_count': len(data),
                'before_memory_mb': round(before_memory_mb, 4),
                'after_memory_mb': round(after_memory_mb, 4),
                'memory_delta_mb': round(
                    after_memory_mb - before_memory_mb,
                    4,
                ),
            }
        ]
    )
    return metric_data


def run_benchmark(data: pd.DataFrame, vector_size: int) -> pd.DataFrame:
    """Run memory usage benchmark.
    Args:
        data (pd.DataFrame): DataFrame with vectors.
        vector_size (int): Size of each vector."""
    faiss_metric_data = measure_faiss(
        data=data,
        vector_size=vector_size,
    )
    qdrant_metric_data = measure_qdrant(
        data=data,
        vector_size=vector_size,
    )

    benchmark_results = pd.concat(
        [faiss_metric_data, qdrant_metric_data],
        ignore_index=True,
    )
    return benchmark_results


if __name__ == '__main__':
    embedding_size = 384

    documents_data = build_documents(rows_count=10000)
    vectors_data = create_vectors(
        data=documents_data,
        vector_size=embedding_size,
    )

    memory_usage_results = run_benchmark(
        data=vectors_data,
        vector_size=embedding_size,
    )

    print('Memory usage benchmark results:')
    print(memory_usage_results.to_string(index=False))
