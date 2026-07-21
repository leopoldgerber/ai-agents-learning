from typing import TypedDict


class ClaimRecord(TypedDict):
    """Store one evaluated answer claim."""

    text: str
    supported: bool
    cited: bool


class GenerationCase(TypedDict):
    """Store one generation evaluation case."""

    question: str
    answer: str
    relevance_terms: list[str]
    reference_terms: list[str]
    claims: list[ClaimRecord]


class GenerationMetrics(TypedDict):
    """Store metrics for one generation case."""

    question: str
    faithfulness: float
    answer_relevance: float
    correctness: float
    citation_rate: float


class GenerationSummary(TypedDict):
    """Store aggregated generation metrics."""

    results: list[GenerationMetrics]
    mean_faithfulness: float
    mean_answer_relevance: float
    mean_correctness: float
    mean_citation_rate: float


def calculate_coverage(
    text: str,
    expected_terms: list[str],
) -> float:
    """Calculate expected term coverage in text.
    Args:
        text (str): Text to evaluate.
        expected_terms (list[str]): Terms expected in the text."""
    if not expected_terms:
        return 0.0

    normalized_text = text.lower()
    found_terms = sum(
        1
        for term in expected_terms
        if term.lower() in normalized_text
    )

    return found_terms / len(expected_terms)


def calculate_faithfulness(
    claims: list[ClaimRecord],
) -> float:
    """Calculate supported claim ratio.
    Args:
        claims (list[ClaimRecord]): Evaluated answer claims."""
    if not claims:
        return 0.0

    supported_claims = sum(
        1 for claim in claims if claim['supported']
    )

    return supported_claims / len(claims)


def calculate_relevance(
    answer: str,
    relevance_terms: list[str],
) -> float:
    """Calculate simplified answer relevance.
    Args:
        answer (str): Generated answer.
        relevance_terms (list[str]): Question-related terms."""
    return calculate_coverage(
        text=answer,
        expected_terms=relevance_terms,
    )


def calculate_correctness(
    answer: str,
    reference_terms: list[str],
) -> float:
    """Calculate simplified answer correctness.
    Args:
        answer (str): Generated answer.
        reference_terms (list[str]): Expected reference terms."""
    return calculate_coverage(
        text=answer,
        expected_terms=reference_terms,
    )


def calculate_citation_rate(
    claims: list[ClaimRecord],
) -> float:
    """Calculate correctly cited claim ratio.
    Args:
        claims (list[ClaimRecord]): Evaluated answer claims."""
    if not claims:
        return 0.0

    cited_claims = sum(
        1
        for claim in claims
        if claim['cited'] and claim['supported']
    )

    return cited_claims / len(claims)


def evaluate_generation(
    test_cases: list[GenerationCase],
) -> GenerationSummary:
    """Evaluate generation quality across test cases.
    Args:
        test_cases (list[GenerationCase]): Generation test cases."""
    if not test_cases:
        return {
            'results': [],
            'mean_faithfulness': 0.0,
            'mean_answer_relevance': 0.0,
            'mean_correctness': 0.0,
            'mean_citation_rate': 0.0,
        }

    case_results: list[GenerationMetrics] = []

    for test_case in test_cases:
        case_results.append(
            {
                'question': test_case['question'],
                'faithfulness': calculate_faithfulness(
                    claims=test_case['claims'],
                ),
                'answer_relevance': calculate_relevance(
                    answer=test_case['answer'],
                    relevance_terms=test_case['relevance_terms'],
                ),
                'correctness': calculate_correctness(
                    answer=test_case['answer'],
                    reference_terms=test_case['reference_terms'],
                ),
                'citation_rate': calculate_citation_rate(
                    claims=test_case['claims'],
                ),
            }
        )

    case_count = len(case_results)

    return {
        'results': case_results,
        'mean_faithfulness': sum(
            result['faithfulness'] for result in case_results
        ) / case_count,
        'mean_answer_relevance': sum(
            result['answer_relevance'] for result in case_results
        ) / case_count,
        'mean_correctness': sum(
            result['correctness'] for result in case_results
        ) / case_count,
        'mean_citation_rate': sum(
            result['citation_rate'] for result in case_results
        ) / case_count,
    }


def print_metrics(
    summary: GenerationSummary,
) -> GenerationSummary:
    """Print generation metrics and return the summary.
    Args:
        summary (GenerationSummary): Calculated generation metrics."""
    for result in summary['results']:
        print(result['question'])
        print(f"Faithfulness: {result['faithfulness']:.3f}")
        print(
            f"Answer Relevance: "
            f"{result['answer_relevance']:.3f}"
        )
        print(f"Correctness: {result['correctness']:.3f}")
        print(f"Citation Rate: {result['citation_rate']:.3f}")
        print('')

    print(
        f"Mean Faithfulness: "
        f"{summary['mean_faithfulness']:.3f}"
    )
    print(
        f"Mean Answer Relevance: "
        f"{summary['mean_answer_relevance']:.3f}"
    )
    print(
        f"Mean Correctness: "
        f"{summary['mean_correctness']:.3f}"
    )
    print(
        f"Mean Citation Rate: "
        f"{summary['mean_citation_rate']:.3f}"
    )

    return summary


if __name__ == '__main__':
    generation_cases: list[GenerationCase] = [
        {
            'question': 'Aus welchen Teilen besteht RAG?',
            'answer': (
                'RAG besteht aus Retrieval und Generation. '
                'Der Retriever sucht relevante Dokumente.'
            ),
            'relevance_terms': [
                'rag',
                'retrieval',
                'generation',
            ],
            'reference_terms': [
                'retrieval',
                'generation',
            ],
            'claims': [
                {
                    'text': (
                        'RAG besteht aus Retrieval und Generation.'
                    ),
                    'supported': True,
                    'cited': True,
                },
                {
                    'text': (
                        'Der Retriever sucht relevante Dokumente.'
                    ),
                    'supported': True,
                    'cited': False,
                },
            ],
        },
        {
            'question': 'Warum wird Faithfulness gemessen?',
            'answer': (
                'Faithfulness prüft, ob Aussagen durch den '
                'bereitgestellten Kontext gestützt werden.'
            ),
            'relevance_terms': [
                'faithfulness',
                'kontext',
            ],
            'reference_terms': [
                'aussagen',
                'kontext',
                'gestützt',
            ],
            'claims': [
                {
                    'text': (
                        'Faithfulness prüft die Unterstützung '
                        'durch den Kontext.'
                    ),
                    'supported': True,
                    'cited': True,
                },
            ],
        },
    ]

    generation_summary = evaluate_generation(
        test_cases=generation_cases,
    )
    displayed_summary = print_metrics(
        summary=generation_summary,
    )
