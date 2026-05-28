import weaviate
import weaviate.classes.config as Configure
from sentence_transformers import SentenceTransformer


def build_client() -> weaviate.WeaviateClient:
    """Build local Weaviate client.
    Args:
        None (type): No arguments."""
    client = weaviate.connect_to_local()
    return client


def create_collection(
    client: weaviate.WeaviateClient,
    collection_name: str,
) -> str:
    """Create Weaviate collection.
    Args:
        client (weaviate.WeaviateClient): Connected client.
        collection_name (str): Collection name."""
    existing_collections = client.collections.list_all()

    if collection_name in existing_collections:
        client.collections.delete(collection_name)

    client.collections.create(
        name=collection_name,
        properties=[
            Configure.Property(
                name='title',
                data_type=Configure.DataType.TEXT,
            ),
            Configure.Property(
                name='content',
                data_type=Configure.DataType.TEXT,
            ),
            Configure.Property(
                name='category',
                data_type=Configure.DataType.TEXT,
            ),
        ],
    )
    return collection_name


def insert_objects(
    client: weaviate.WeaviateClient,
    collection_name: str,
    model_name: str,
) -> str:
    """Insert objects with manual vectors.
    Args:
        client (weaviate.WeaviateClient): Connected client.
        collection_name (str): Collection name.
        model_name (str): SentenceTransformer model name."""
    model = SentenceTransformer(model_name)
    collection = client.collections.get(collection_name)

    items_list = [
        {
            'title': 'MSU',
            'content': 'Moscow State University was founded in 1755.',
            'category': 'education',
        },
        {
            'title': 'FAISS',
            'content': 'FAISS is a lightweight vector search library.',
            'category': 'rag',
        },
        {
            'title': 'Weaviate',
            'content': 'Weaviate is a vector database for production use.',
            'category': 'rag',
        },
    ]

    with collection.batch.dynamic() as batch:
        for item in items_list:
            item_vector = model.encode(item['content']).tolist()
            batch.add_object(
                properties=item,
                vector=item_vector,
            )

    return collection_name


def search_objects(
    client: weaviate.WeaviateClient,
    collection_name: str,
    model_name: str,
    query_text: str,
    limit_value: int,
) -> list:
    """Search objects by semantic similarity.
    Args:
        client (weaviate.WeaviateClient): Connected client.
        collection_name (str): Collection name.
        model_name (str): SentenceTransformer model name.
        query_text (str): Query text.
        limit_value (int): Number of results."""
    model = SentenceTransformer(model_name)
    collection = client.collections.get(collection_name)
    query_vector = model.encode(query_text).tolist()

    response = collection.query.near_vector(
        near_vector=query_vector,
        limit=limit_value,
        return_properties=['title', 'category'],
    )
    return response.objects


def print_objects(objects_list: list) -> list:
    """Print found objects and properties.
    Args:
        objects_list (list): Search results."""
    for index, obj_item in enumerate(objects_list, start=1):
        print(f'Result {index}:')
        print(obj_item.properties)
        print('-' * 40)

    return objects_list


if __name__ == '__main__':
    client = build_client()

    try:
        collection_name = create_collection(
            client=client,
            collection_name='ArticleIndex',
        )
        inserted_name = insert_objects(
            client=client,
            collection_name=collection_name,
            model_name='BAAI/bge-m3',
        )
        objects_list = search_objects(
            client=client,
            collection_name=inserted_name,
            model_name='BAAI/bge-m3',
            query_text='vector database for retrieval',
            limit_value=2,
        )
        printed_objects = print_objects(objects_list=objects_list)
    finally:
        client.close()
