import re


def count_words(query: str) -> int:
    """Count words in query.
    Args:
        query (str): Input user query."""
    words_list = query.split()
    word_count = len(words_list)

    return word_count


def has_question_words(
    query: str,
    question_words: list[str],
) -> bool:
    """Check whether query contains question words.
    Args:
        query (str): Input user query.
        question_words (list[str]): Question words for matching."""
    lowered_query = query.lower()

    has_words = any(
        word_value in lowered_query
        for word_value in question_words
    )
    return has_words


def has_technical_terms(query: str) -> bool:
    """Check whether query contains technical-looking terms.
    Args:
        query (str): Input user query."""
    technical_pattern = re.compile(r'[A-Za-z]+[-_][A-Za-z0-9]+|[A-Z]{2,}')
    has_terms = bool(technical_pattern.search(query))

    return has_terms


def calculate_budget(
    query: str,
    base_budget: float,
    max_multiplier: float,
) -> float:
    """Calculate adaptive time budget for query.
    Args:
        query (str): Input user query.
        base_budget (float): Base budget in seconds.
        max_multiplier (float): Maximum budget multiplier."""
    budget_value = base_budget
    word_count = count_words(query=query)

    if word_count > 15:
        budget_value *= 1.5
    elif word_count > 8:
        budget_value *= 1.2

    question_words = [
        'how',
        'why',
        'wie',
        'warum',
        'как',
        'почему',
    ]

    if has_question_words(
        query=query,
        question_words=question_words,
    ):
        budget_value *= 1.3

    if has_technical_terms(query=query):
        budget_value *= 1.2

    max_budget = base_budget * max_multiplier
    final_budget = min(budget_value, max_budget)

    return round(final_budget, 3)


def build_examples() -> list[str]:
    """Build example queries for adaptive budget.
    Args:
        None: No arguments."""
    queries_list = [
        'BM25 definition',
        'Warum verbessert Hybrid-Search die Retrieval-Qualität?',
        (
            'How does cross-encoder reranking improve precision '
            'after bi-encoder retrieval in a RAG pipeline?'
        ),
        'IVF-PQ',
    ]
    return queries_list


def print_budgets(
    queries_list: list[str],
    base_budget: float,
    max_multiplier: float,
) -> list[float]:
    """Print adaptive budgets for queries.
    Args:
        queries_list (list[str]): Queries for budget calculation.
        base_budget (float): Base budget in seconds.
        max_multiplier (float): Maximum budget multiplier."""
    budgets_list = []

    for query_text in queries_list:
        budget_value = calculate_budget(
            query=query_text,
            base_budget=base_budget,
            max_multiplier=max_multiplier,
        )
        budgets_list.append(budget_value)
        print(f'Query: {query_text}')
        print(f'Budget: {budget_value} seconds')
        print('-' * 40)

    return budgets_list


if __name__ == '__main__':
    queries_list = build_examples()
    budgets_list = print_budgets(
        queries_list=queries_list,
        base_budget=1.5,
        max_multiplier=2.5,
    )
