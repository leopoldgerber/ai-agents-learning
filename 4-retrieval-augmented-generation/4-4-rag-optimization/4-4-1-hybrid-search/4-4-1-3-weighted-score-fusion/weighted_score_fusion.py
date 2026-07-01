import numpy as np


def build_scores() -> tuple[dict[str, float], dict[str, float]]:
    """Build sample BM25 and vector search scores.
    Args:
        None: No arguments."""
    bm25_scores = {
        'doc_1': 8.5,
        'doc_2': 6.2,
        'doc_3': 4.0,
    }
    vector_scores = {
        'doc_2': 0.92,
        'doc_4': 0.88,
        'doc_1': 0.70,
    }

    return bm25_scores, vector_scores


def normalize_scores(scores_map: dict[str, float]) -> dict[str, float]:
    """Normalize scores to range from zero to one.
    Args:
        scores_map (dict[str, float]): Scores by document id."""
    if not scores_map:
        return {}

    keys_list = list(scores_map.keys())
    values_array = np.array(
        list(scores_map.values()),
        dtype=float,
    )

    min_value = float(values_array.min())
    max_value = float(values_array.max())

    if max_value == min_value:
        return {
            doc_id: 1.0
            for doc_id in keys_list
        }

    normalized_array = (values_array - min_value) / (
        max_value - min_value
    )

    normalized_scores = {
        doc_id: float(score_value)
        for doc_id, score_value in zip(keys_list, normalized_array)
    }
    return normalized_scores


def fuse_scores(
    bm25_scores: dict[str, float],
    vector_scores: dict[str, float],
    alpha_value: float,
) -> dict[str, float]:
    """Fuse normalized BM25 and vector scores.
    Args:
        bm25_scores (dict[str, float]): BM25 scores by document id.
        vector_scores (dict[str, float]): Vector scores by document id.
        alpha_value (float): Weight for BM25 scores."""
    bm25_normalized = normalize_scores(scores_map=bm25_scores)
    vector_normalized = normalize_scores(scores_map=vector_scores)

    all_doc_ids = set(bm25_normalized) | set(vector_normalized)
    fused_scores = {}

    for doc_id in all_doc_ids:
        bm25_value = bm25_normalized.get(doc_id, 0.0)
        vector_value = vector_normalized.get(doc_id, 0.0)

        fused_scores[doc_id] = (
            alpha_value * bm25_value
            + (1.0 - alpha_value) * vector_value
        )

    return fused_scores


def sort_scores(
    fused_scores: dict[str, float],
) -> list[tuple[str, float]]:
    """Sort fused scores from highest to lowest.
    Args:
        fused_scores (dict[str, float]): Fused scores by document id."""
    sorted_scores = sorted(
        fused_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    return sorted_scores


def print_results(
    sorted_scores: list[tuple[str, float]],
) -> list[tuple[str, float]]:
    """Print weighted fusion results.
    Args:
        sorted_scores (list[tuple[str, float]]): Ranked fused scores."""
    for rank_index, (doc_id, score_value) in enumerate(
        sorted_scores,
        start=1,
    ):
        print(
            f'Rank {rank_index}: '
            f'{doc_id} | fused_score={score_value:.4f}'
        )

    return sorted_scores


if __name__ == '__main__':
    bm25_scores, vector_scores = build_scores()

    fused_scores = fuse_scores(
        bm25_scores=bm25_scores,
        vector_scores=vector_scores,
        alpha_value=0.6,
    )
    sorted_scores = sort_scores(fused_scores=fused_scores)
    printed_scores = print_results(sorted_scores=sorted_scores)
