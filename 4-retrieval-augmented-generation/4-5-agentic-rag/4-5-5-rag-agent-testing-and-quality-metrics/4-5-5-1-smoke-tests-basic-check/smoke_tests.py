from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def build_cases() -> list[dict[str, object]]:
    """Build smoke test cases.
    Args:
        None: No arguments."""
    test_cases = [
        {
            'name': 'Simple question without retrieval',
            'query': 'Привет!',
            'should_retrieve': False,
        },
        {
            'name': 'Question that needs retrieval',
            'query': 'Что такое LangGraph?',
            'should_retrieve': True,
        },
        {
            'name': 'Long question',
            'query': 'Объясни архитектуру LangGraph и её компоненты',
            'should_retrieve': True,
        },
    ]
    return test_cases


def invoke_agent(query: str) -> dict[str, list[object]]:
    """Run sample agent response.
    Args:
        query (str): User query."""
    messages = [
        HumanMessage(content=query),
    ]

    needs_retrieval = 'LangGraph' in query

    if needs_retrieval:
        messages.append(
            ToolMessage(
                content='LangGraph builds cyclic agent workflows.',
                tool_call_id='demo_tool_call',
                name='knowledge_base_search',
            ),
        )

    messages.append(
        AIMessage(content='Agent response for smoke testing.'),
    )

    return {'messages': messages}


def detect_retrieval(response: dict[str, Any]) -> bool:
    """Detect whether response contains tool messages.
    Args:
        response (dict[str, Any]): Agent response state."""
    messages = response.get('messages', [])

    retrieved = any(
        getattr(message_item, 'type', '') == 'tool'
        for message_item in messages
    )
    return retrieved


def check_response(
    response: dict[str, Any],
    expected_retrieval: bool,
) -> tuple[bool, list[str]]:
    """Check basic response validity.
    Args:
        response (dict[str, Any]): Agent response state.
        expected_retrieval (bool): Expected retrieval route."""
    errors_list = []

    if response is None:
        errors_list.append('Response is missing.')
        return False, errors_list

    if 'messages' not in response:
        errors_list.append('Messages key is missing.')
        return False, errors_list

    messages = response.get('messages', [])

    if not messages:
        errors_list.append('Messages list is empty.')
        return False, errors_list

    final_message = messages[-1]
    final_content = str(getattr(final_message, 'content', ''))

    if not final_content:
        errors_list.append('Final message content is empty.')

    retrieved = detect_retrieval(response=response)

    if retrieved != expected_retrieval:
        errors_list.append(
            'Retrieval route does not match expectation.'
        )

    passed = not errors_list
    return passed, errors_list


def run_case(test_case: dict[str, object]) -> dict[str, object]:
    """Run one smoke test case.
    Args:
        test_case (dict[str, object]): Smoke test case."""
    query = str(test_case['query'])
    expected_retrieval = bool(test_case['should_retrieve'])

    try:
        response = invoke_agent(query=query)
        passed, errors_list = check_response(
            response=response,
            expected_retrieval=expected_retrieval,
        )

        status = 'PASSED' if passed else 'FAILED'
        retrieved = detect_retrieval(response=response)

        result = {
            'test': str(test_case['name']),
            'status': status,
            'retrieved': retrieved,
            'errors': errors_list,
        }
        return result

    except Exception as error:
        return {
            'test': str(test_case['name']),
            'status': 'FAILED',
            'retrieved': False,
            'errors': [str(error)],
        }


def run_tests(test_cases: list[dict[str, object]]) -> list[dict[str, object]]:
    """Run all smoke test cases.
    Args:
        test_cases (list[dict[str, object]]): Smoke test cases."""
    results_list = []

    for test_case in test_cases:
        result = run_case(test_case=test_case)
        results_list.append(result)

    return results_list


def print_results(
    results_list: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Print smoke test results.
    Args:
        results_list (list[dict[str, object]]): Smoke test results."""
    for result_item in results_list:
        print(f'Test: {result_item["test"]}')
        print(f'Status: {result_item["status"]}')
        print(f'Retrieval: {result_item["retrieved"]}')

        errors_list = result_item.get('errors', [])

        if errors_list:
            print('Errors:')
            for error_text in errors_list:
                print(f'- {error_text}')

        print('-' * 40)

    return results_list


def print_summary(
    results_list: list[dict[str, object]],
) -> dict[str, int]:
    """Print smoke test summary.
    Args:
        results_list (list[dict[str, object]]): Smoke test results."""
    passed_count = sum(
        1
        for result_item in results_list
        if result_item['status'] == 'PASSED'
    )
    total_count = len(results_list)

    print(f'Results: {passed_count}/{total_count} tests passed')

    summary = {
        'passed': passed_count,
        'total': total_count,
    }
    return summary


if __name__ == '__main__':
    test_cases = build_cases()
    results_list = run_tests(test_cases=test_cases)
    printed_results = print_results(results_list=results_list)
    test_summary = print_summary(results_list=results_list)
