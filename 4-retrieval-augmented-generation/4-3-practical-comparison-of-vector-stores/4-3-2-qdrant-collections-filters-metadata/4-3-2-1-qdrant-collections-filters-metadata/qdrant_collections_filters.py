from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import FieldCondition
from qdrant_client.models import Filter
from qdrant_client.models import MatchValue
from qdrant_client.models import PointStruct
from qdrant_client.models import Range
from qdrant_client.models import ScoredPoint
from qdrant_client.models import VectorParams


def build_client(url: str) -> QdrantClient:
    """Build Qdrant client.
    Args:
        url (str): Qdrant server URL."""
    client = QdrantClient(url=url)
    return client


def recreate_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> str:
    """Recreate collection for vector search.
    Args:
        client (QdrantClient): Connected Qdrant client.
        collection_name (str): Collection name.
        vector_size (int): Vector dimension size."""
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )
    return collection_name


def build_points() -> list[PointStruct]:
    """Build sample points with payload.
    Args:
        None: No arguments."""
    points_list = [
        PointStruct(
            id=1,
            vector=[0.10, 0.20, 0.30, 0.40],
            payload={
                'title': 'Intro to machine learning',
                'year': 2023,
                'category': 'AI',
                'language': 'en',
                'tags': ['ML', 'Python'],
            },
        ),
        PointStruct(
            id=2,
            vector=[0.12, 0.21, 0.32, 0.41],
            payload={
                'title': 'Neural networks in practice',
                'year': 2024,
                'category': 'Deep Learning',
                'language': 'en',
                'tags': ['DL', 'Python'],
            },
        ),
        PointStruct(
            id=3,
            vector=[0.80, 0.10, 0.15, 0.20],
            payload={
                'title': 'Russian RAG tutorial',
                'year': 2024,
                'category': 'AI',
                'language': 'ru',
                'tags': ['RAG', 'Python'],
            },
        ),
    ]
    return points_list


def upsert_points(
    client: QdrantClient,
    collection_name: str,
    points_list: list[PointStruct],
) -> list[PointStruct]:
    """Upload points into Qdrant collection.
    Args:
        client (QdrantClient): Connected Qdrant client.
        collection_name (str): Collection name.
        points_list (list[PointStruct]): Points for uploading."""
    client.upsert(
        collection_name=collection_name,
        points=points_list,
    )
    return points_list


def build_filter(
    category_name: str,
    min_year: int,
) -> Filter:
    """Build payload filter for search.
    Args:
        category_name (str): Required document category.
        min_year (int): Minimum publication year."""
    search_filter = Filter(
        must=[
            FieldCondition(
                key='category',
                match=MatchValue(value=category_name),
            ),
            FieldCondition(
                key='year',
                range=Range(gte=min_year),
            ),
        ],
    )
    return search_filter


def search_points(
    client: QdrantClient,
    collection_name: str,
    query_vector: list[float],
    search_filter: Filter,
    limit_value: int,
) -> list[ScoredPoint]:
    """Search points with vector and payload filter.
    Args:
        client (QdrantClient): Connected Qdrant client.
        collection_name (str): Collection name.
        query_vector (list[float]): Query vector.
        search_filter (Filter): Payload filter.
        limit_value (int): Number of search results."""
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=search_filter,
        limit=limit_value,
    )
    return search_result


def print_results(search_result: list[ScoredPoint]) -> list[ScoredPoint]:
    """Print search results with payload.
    Args:
        search_result (list[ScoredPoint]): Qdrant search results."""
    for point_item in search_result:
        print(
            {
                'id': point_item.id,
                'score': point_item.score,
                'title': point_item.payload.get('title'),
                'year': point_item.payload.get('year'),
                'category': point_item.payload.get('category'),
            },
        )

    return search_result


if __name__ == '__main__':
    client = build_client(url='http://localhost:6333')
    collection_name = recreate_collection(
        client=client,
        collection_name='my_documents',
        vector_size=4,
    )
    points_list = build_points()
    uploaded_points = upsert_points(
        client=client,
        collection_name=collection_name,
        points_list=points_list,
    )
    search_filter = build_filter(
        category_name='AI',
        min_year=2023,
    )
    search_result = search_points(
        client=client,
        collection_name=collection_name,
        query_vector=[0.11, 0.19, 0.29, 0.39],
        search_filter=search_filter,
        limit_value=5,
    )
    printed_result = print_results(search_result=search_result)
