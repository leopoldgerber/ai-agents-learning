from typing import Any
import weaviate


def connect_client() -> Any:
    """Connect to local Weaviate instance.
    Args:
        None: No arguments."""
    client = weaviate.connect_to_local()
    return client


def search_hybrid(
    client: Any,
    collection_name: str,
    query: str,
    alpha_value: float,
    result_count: int,
) -> list[dict[str, Any]]:
    """Run native hybrid search in Weaviate.
    Args:
        client (Any): Connected Weaviate client.
        collection_name (str): Collection name for search.
        query (str): User search query.
        alpha_value (float): Vector search relative weight.
        result_count (int): Number of search results."""
    collection = client.collections.use(collection_name)

    response = collection.query.hybrid(
        query=query,
        alpha=alpha_value,
        limit=result_count,
    )

    results_list = [
        dict(result_object.properties)
        for result_object in response.objects
    ]
    return results_list


def print_results(
    results_list: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Print native hybrid search results.
    Args:
        results_list (list[dict[str, Any]]): Hybrid search results."""
    for rank_index, result_item in enumerate(
        results_list,
        start=1,
    ):
        print(f'Rank {rank_index}:')
        print(result_item)
        print('-' * 40)

    return results_list


if __name__ == '__main__':
    client = connect_client()

    try:
        results_list = search_hybrid(
            client=client,
            collection_name='RagDocument',
            query='machine learning with Python',
            alpha_value=0.5,
            result_count=5,
        )
        printed_results = print_results(
            results_list=results_list,
        )
    finally:
        client.close()
