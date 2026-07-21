from collections.abc import Callable
from typing import TypedDict


class TestCase(TypedDict):
    """Store one automatic evaluation test case."""

    question: str
    expected_terms: list[str]
    relevant_docs: list[str]
    should_cite: bool


class AgentResult(TypedDict):
    """Store one RAG agent result."""

    answer: str
    retrieved_docs: list[str]
    cited_docs: list[str]


class CaseResult(TypedDict):
    """Store metrics for one evaluated test case."""

    question: str
    retrieval_hit: bool
    answer_score: float
    citation_ok: bool
    reciprocal_rank: float
    passed: bool


class EvaluationSummary(TypedDict):
    """Store aggregated dataset evaluation metrics."""

    results: list[CaseResult]
    pass_rate: float
    retrieval_hit_rate: float
    mean_answer_score: float
    citation_rate: float
    citation_compliance: float
    mrr: float


def calculate_answer_score(
    answer: str,
    expected_terms: list[str],
) -> float:
    """Calculate expected term coverage.
    Args:
        answer (str): Generated answer.
        expected_terms (list[str]): Expected answer terms."""
    if not expected_terms:
        return 1.0

    normalized_answer = answer.lower()
    found_terms = sum(
        1
        for term in expected_terms
        if term.lower() in normalized_answer
    )

    return found_terms / len(expected_terms)


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


def evaluate_test_case(
    test_case: TestCase,
    agent_result: AgentResult,
) -> CaseResult:
    """Evaluate one RAG test case.
    Args:
        test_case (TestCase): Expected test data.
        agent_result (AgentResult): Actual agent output."""
    relevant_set = set(test_case['relevant_docs'])
    retrieved_set = set(agent_result['retrieved_docs'])

    retrieval_hit = bool(relevant_set & retrieved_set)
    retrieval_ok = retrieval_hit or not relevant_set

    answer_score = calculate_answer_score(
        answer=agent_result['answer'],
        expected_terms=test_case['expected_terms'],
    )
    answer_ok = answer_score >= 0.5

    has_citations = bool(agent_result['cited_docs'])
    citation_ok = has_citations == test_case['should_cite']

    reciprocal_rank = calculate_reciprocal_rank(
        retrieved_docs=agent_result['retrieved_docs'],
        relevant_docs=test_case['relevant_docs'],
    )

    return {
        'question': test_case['question'],
        'retrieval_hit': retrieval_hit,
        'answer_score': answer_score,
        'citation_ok': citation_ok,
        'reciprocal_rank': reciprocal_rank,
        'passed': retrieval_ok and answer_ok and citation_ok,
    }


def evaluate_dataset(
    test_cases: list[TestCase],
    agent_runner: Callable[[str], AgentResult],
) -> EvaluationSummary:
    """Evaluate a RAG agent on a test dataset.
    Args:
        test_cases (list[TestCase]): Gold evaluation cases.
        agent_runner (Callable): Function returning an agent result."""
    if not test_cases:
        return {
            'results': [],
            'pass_rate': 0.0,
            'retrieval_hit_rate': 0.0,
            'mean_answer_score': 0.0,
            'citation_rate': 0.0,
            'citation_compliance': 0.0,
            'mrr': 0.0,
        }

    results: list[CaseResult] = []
    citation_count = 0

    for test_case in test_cases:
        agent_result = agent_runner(test_case['question'])
        case_result = evaluate_test_case(
            test_case=test_case,
            agent_result=agent_result,
        )
        results.append(case_result)

        if agent_result['cited_docs']:
            citation_count += 1

    case_count = len(results)

    return {
        'results': results,
        'pass_rate': sum(
            result['passed'] for result in results
        ) / case_count,
        'retrieval_hit_rate': sum(
            result['retrieval_hit'] for result in results
        ) / case_count,
        'mean_answer_score': sum(
            result['answer_score'] for result in results
        ) / case_count,
        'citation_rate': citation_count / case_count,
        'citation_compliance': sum(
            result['citation_ok'] for result in results
        ) / case_count,
        'mrr': sum(
            result['reciprocal_rank'] for result in results
        ) / case_count,
    }


def print_report(
    summary: EvaluationSummary,
) -> EvaluationSummary:
    """Print evaluation results and return the summary.
    Args:
        summary (EvaluationSummary): Aggregated evaluation metrics."""
    for result in summary['results']:
        status = 'PASSED' if result['passed'] else 'FAILED'
        question = result['question']
        answer_score = result['answer_score']
        reciprocal_rank = result['reciprocal_rank']
        citation_ok = result['citation_ok']

        print(f'{status}: {question}')
        print(
            f'Answer Score: {answer_score:.3f}, '
            f'RR: {reciprocal_rank:.3f}'
        )
        print(f'Citation OK: {citation_ok}')
        print('')

    pass_rate = summary['pass_rate']
    retrieval_hit_rate = summary['retrieval_hit_rate']
    mean_answer_score = summary['mean_answer_score']
    citation_rate = summary['citation_rate']
    citation_compliance = summary['citation_compliance']
    mean_reciprocal_rank = summary['mrr']

    print(f'Pass Rate: {pass_rate:.1%}')
    print(f'Retrieval Hit Rate: {retrieval_hit_rate:.1%}')
    print(f'Mean Answer Score: {mean_answer_score:.3f}')
    print(f'Citation Rate: {citation_rate:.1%}')
    print(f'Citation Compliance: {citation_compliance:.1%}')
    print(f'MRR: {mean_reciprocal_rank:.3f}')

    return summary


def run_demo_agent(
    question: str,
) -> AgentResult:
    """Return deterministic demo agent output.
    Args:
        question (str): Test question."""
    if question == 'Was ist LangGraph?':
        return {
            'answer': (
                'LangGraph ist ein Framework für graphbasierte '
                'Agent-Workflows.'
            ),
            'retrieved_docs': ['doc4', 'doc2'],
            'cited_docs': ['doc2'],
        }

    if question == 'Wofür wird RAG verwendet?':
        return {
            'answer': (
                'RAG verbindet Retrieval, Generation und externe '
                'Wissensquellen.'
            ),
            'retrieved_docs': ['doc3', 'doc8'],
            'cited_docs': ['doc3'],
        }

    return {
        'answer': 'Hallo!',
        'retrieved_docs': [],
        'cited_docs': [],
    }


if __name__ == '__main__':
    evaluation_cases: list[TestCase] = [
        {
            'question': 'Was ist LangGraph?',
            'expected_terms': [
                'graph',
                'workflow',
                'agent',
            ],
            'relevant_docs': ['doc2'],
            'should_cite': True,
        },
        {
            'question': 'Wofür wird RAG verwendet?',
            'expected_terms': [
                'retrieval',
                'generation',
                'wissen',
            ],
            'relevant_docs': ['doc3'],
            'should_cite': True,
        },
        {
            'question': 'Hallo, wie geht es dir?',
            'expected_terms': [],
            'relevant_docs': [],
            'should_cite': False,
        },
    ]

    evaluation_summary = evaluate_dataset(
        test_cases=evaluation_cases,
        agent_runner=run_demo_agent,
    )
    displayed_summary = print_report(
        summary=evaluation_summary,
    )
