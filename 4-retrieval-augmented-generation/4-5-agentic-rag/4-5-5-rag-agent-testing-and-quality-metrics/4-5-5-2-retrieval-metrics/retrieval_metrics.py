from typing import TypedDict


class RetrievalCase(TypedDict):
    """Store one retrieval evaluation case."""

    question: str
    retrieved_docs: list[str]
    relevant_docs: list[str]


class CaseMetrics(TypedDict):
    """Store metrics for one retrieval case."""

    question: str
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float


class RetrievalSummary(TypedDict):
    """Store aggregated retrieval metrics."""

    results: list[CaseMetrics]
    mean_precision_at_k: float
    mean_recall_at_k: float
    mrr: float


def calculate_precision(
    retrieved_docs: list[str],
    relevant_docs: list[str],
    k: int,
) -> float:
    """Calculate precision at a fixed cutoff.
    Args:
        retrieved_docs (list[str]): Ranked retrieved document IDs.
        relevant_docs (list[str]): Gold relevant document IDs.
        k (int): Number of top results to evaluate."""
    if k <= 0:
        return 0.0

    retrieved_top_k = set(retrieved_docs[:k])
    relevant_set = set(relevant_docs)
    relevant_found = len(retrieved_top_k & relevant_set)

    return relevant_found / k


def calculate_recall(
    retrieved_docs: list[str],
    relevant_docs: list[str],
    k: int,
) -> float:
    """Calculate recall at a fixed cutoff.
    Args:
        retrieved_docs (list[str]): Ranked retrieved document IDs.
        relevant_docs (list[str]): Gold relevant document IDs.
        k (int): Number of top results to evaluate."""
    if k <= 0 or not relevant_docs:
        return 0.0

    retrieved_top_k = set(retrieved_docs[:k])
    relevant_set = set(relevant_docs)
    relevant_found = len(retrieved_top_k & relevant_set)

    return relevant_found / len(relevant_set)


def calculate_reciprocal_rank(
    retrieved_docs: list[str],
    relevant_docs: list[str],
) -> float:
    """Calculate reciprocal rank for one query.
    Args:
        retrieved_docs (list[str]): Ranked retrieved document IDs.
        relevant_docs (list[str]): Gold relevant document IDs."""
    relevant_set = set(relevant_docs)

    for rank, document_id in enumerate(retrieved_docs, start=1):
        if document_id in relevant_set:
            return 1.0 / rank

    return 0.0


def evaluate_retrieval(
    test_cases: list[RetrievalCase],
    k: int,
) -> RetrievalSummary:
    """Evaluate retrieval quality across test cases.
    Args:
        test_cases (list[RetrievalCase]): Retrieval test cases.
        k (int): Number of top results to evaluate."""
    if not test_cases:
        return {
            'results': [],
            'mean_precision_at_k': 0.0,
            'mean_recall_at_k': 0.0,
            'mrr': 0.0,
        }

    case_results: list[CaseMetrics] = []

    for test_case in test_cases:
        precision_score = calculate_precision(
            retrieved_docs=test_case['retrieved_docs'],
            relevant_docs=test_case['relevant_docs'],
            k=k,
        )
        recall_score = calculate_recall(
            retrieved_docs=test_case['retrieved_docs'],
            relevant_docs=test_case['relevant_docs'],
            k=k,
        )
        reciprocal_rank = calculate_reciprocal_rank(
            retrieved_docs=test_case['retrieved_docs'],
            relevant_docs=test_case['relevant_docs'],
        )

        case_results.append(
            {
                'question': test_case['question'],
                'precision_at_k': precision_score,
                'recall_at_k': recall_score,
                'reciprocal_rank': reciprocal_rank,
            }
        )

    case_count = len(case_results)
    mean_precision = sum(
        result['precision_at_k'] for result in case_results
    ) / case_count
    mean_recall = sum(
        result['recall_at_k'] for result in case_results
    ) / case_count
    mean_reciprocal_rank = sum(
        result['reciprocal_rank'] for result in case_results
    ) / case_count

    return {
        'results': case_results,
        'mean_precision_at_k': mean_precision,
        'mean_recall_at_k': mean_recall,
        'mrr': mean_reciprocal_rank,
    }


def print_metrics(
    summary: RetrievalSummary,
    k: int,
) -> RetrievalSummary:
    """Print retrieval metrics and return the summary.
    Args:
        summary (RetrievalSummary): Calculated retrieval metrics.
        k (int): Number of evaluated top results."""
    for result in summary['results']:
        question = result['question']
        precision_score = result['precision_at_k']
        recall_score = result['recall_at_k']
        reciprocal_rank = result['reciprocal_rank']

        print(
            f'{question}: P@{k}={precision_score:.3f}, '
            f'R@{k}={recall_score:.3f}, '
            f'RR={reciprocal_rank:.3f}'
        )

    mean_precision = summary['mean_precision_at_k']
    mean_recall = summary['mean_recall_at_k']
    mean_reciprocal_rank = summary['mrr']

    print(f'Mean Precision@{k}: {mean_precision:.3f}')
    print(f'Mean Recall@{k}: {mean_recall:.3f}')
    print(f'MRR: {mean_reciprocal_rank:.3f}')

    return summary


if __name__ == '__main__':
    retrieval_cases: list[RetrievalCase] = [
        {
            'question': 'Was ist LangGraph?',
            'retrieved_docs': ['doc4', 'doc2', 'doc7'],
            'relevant_docs': ['doc2', 'doc5'],
        },
        {
            'question': 'Wofür wird RAG verwendet?',
            'retrieved_docs': ['doc3', 'doc8', 'doc6'],
            'relevant_docs': ['doc3'],
        },
        {
            'question': 'Was bedeutet Agentic RAG?',
            'retrieved_docs': ['doc9', 'doc6', 'doc1'],
            'relevant_docs': ['doc1', 'doc6'],
        },
    ]

    retrieval_summary = evaluate_retrieval(
        test_cases=retrieval_cases,
        k=3,
    )
    displayed_summary = print_metrics(
        summary=retrieval_summary,
        k=3,
    )
