from collections import defaultdict


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


def build_ranks(
    scores_map: dict[str, float],
    higher_better: bool,
) -> dict[str, int]:
    """Convert score map into rank map.
    Args:
        scores_map (dict[str, float]): Scores by document id.
        higher_better (bool): Whether higher score is better."""
    sorted_items = sorted(
        scores_map.items(),
        key=lambda item: item[1],
        reverse=higher_better,
    )

    ranks_map = {
        doc_id: rank_index + 1
        for rank_index, (doc_id, score_value) in enumerate(sorted_items)
    }
    return ranks_map


def fuse_ranks(
    bm25_scores: dict[str, float],
    vector_scores: dict[str, float],
    rrf_k: int,
) -> dict[str, float]:
    """Fuse BM25 and vector rankings with RRF.
    Args:
        bm25_scores (dict[str, float]): BM25 scores by document id.
        vector_scores (dict[str, float]): Vector scores by document id.
        rrf_k (int): RRF smoothing constant."""
    bm25_ranks = build_ranks(
        scores_map=bm25_scores,
        higher_better=True,
    )
    vector_ranks = build_ranks(
        scores_map=vector_scores,
        higher_better=True,
    )

    all_doc_ids = set(bm25_ranks) | set(vector_ranks)
    fused_scores = defaultdict(float)

    for doc_id in all_doc_ids:
        if doc_id in bm25_ranks:
            fused_scores[doc_id] += 1.0 / (rrf_k + bm25_ranks[doc_id])

        if doc_id in vector_ranks:
            fused_scores[doc_id] += 1.0 / (rrf_k + vector_ranks[doc_id])

    return dict(fused_scores)


def sort_fused(
    fused_scores: dict[str, float],
) -> list[tuple[str, float]]:
    """Sort fused RRF scores.
    Args:
        fused_scores (dict[str, float]): RRF scores by document id."""
    sorted_scores = sorted(
        fused_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    return sorted_scores


def print_results(
    sorted_scores: list[tuple[str, float]],
) -> list[tuple[str, float]]:
    """Print ranked RRF results.
    Args:
        sorted_scores (list[tuple[str, float]]): Sorted RRF results."""
    for rank_index, (doc_id, score_value) in enumerate(
        sorted_scores,
        start=1,
    ):
        print(f'Rank {rank_index}: {doc_id} | RRF={score_value:.6f}')

    return sorted_scores


if __name__ == '__main__':
    bm25_scores, vector_scores = build_scores()

    fused_scores = fuse_ranks(
        bm25_scores=bm25_scores,
        vector_scores=vector_scores,
        rrf_k=60,
    )
    sorted_scores = sort_fused(fused_scores=fused_scores)
    printed_scores = print_results(sorted_scores=sorted_scores)
