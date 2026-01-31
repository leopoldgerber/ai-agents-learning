import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:
    should_retry: bool
    delay_s: float
    reason: str


def is_retryable_status(status_code: int) -> bool:
    """Check whether an HTTP status code should be retried.
    Args:
        status_code (int): HTTP status code."""
    if 500 <= status_code <= 599:
        return True
    if status_code == 429:
        return True
    return False


def calc_backoff_delay(
        attempt_index: int, base_delay_s: float, max_delay_s: float) -> float:
    """Calculate exponential backoff delay.
    Args:
        attempt_index (int): Attempt number starting from 1.
        base_delay_s (float): Base delay in seconds.
        max_delay_s (float): Maximum delay in seconds."""
    delay_s = base_delay_s * (2 ** (attempt_index - 1))
    return min(delay_s, max_delay_s)


def decide_retry(
    attempt_index: int,
    max_attempts: int,
    status_code: int | None,
    had_timeout: bool,
    base_delay_s: float,
    max_delay_s: float,
) -> RetryDecision:
    """Decide whether to retry and compute next delay.
    Args:
        attempt_index (int): Attempt number starting from 1.
        max_attempts (int): Maximum number of attempts.
        status_code (int | None): HTTP status code, if available.
        had_timeout (bool): Whether the request timed out.
        base_delay_s (float): Base delay in seconds.
        max_delay_s (float): Maximum delay in seconds."""
    if attempt_index >= max_attempts:
        return RetryDecision(
            should_retry=False,
            delay_s=0.0,
            reason='max attempts reached'
        )

    if had_timeout:
        delay_s = calc_backoff_delay(
            attempt_index=attempt_index,
            base_delay_s=base_delay_s,
            max_delay_s=max_delay_s,
        )
        return RetryDecision(
            should_retry=True,
            delay_s=delay_s,
            reason='timeout'
        )

    if status_code is None:
        return RetryDecision(
            should_retry=False,
            delay_s=0.0,
            reason='missing status code'
        )

    if is_retryable_status(status_code=status_code):
        delay_s = calc_backoff_delay(
            attempt_index=attempt_index,
            base_delay_s=base_delay_s,
            max_delay_s=max_delay_s,
        )
        return RetryDecision(
            should_retry=True,
            delay_s=delay_s,
            reason=f'status {status_code} retryable'
        )

    return RetryDecision(
        should_retry=False,
        delay_s=0.0,
        reason=f'status {status_code} not retryable'
    )


def simulate_delivery(
        outcomes: list[str], max_attempts: int) -> list[dict[str, str]]:
    """Simulate delivery attempts using a predefined outcome list.
    Args:
        outcomes (list[str]):
            Outcomes by attempt: '200', '500', '429', 'timeout'.
        max_attempts (int): Maximum number of attempts."""
    attempt_index = 1
    results: list[dict[str, str]] = []

    while True:
        outcome = (
            outcomes[attempt_index - 1]
            if attempt_index - 1 < len(outcomes) else 'timeout')

        if outcome == 'timeout':
            decision = decide_retry(
                attempt_index=attempt_index,
                max_attempts=max_attempts,
                status_code=None,
                had_timeout=True,
                base_delay_s=0.5,
                max_delay_s=5.0,
            )
            results.append(
                {
                    'attempt': str(attempt_index),
                    'outcome': 'timeout',
                    'decision': decision.reason
                }
            )
        else:
            status_code = int(outcome)
            decision = decide_retry(
                attempt_index=attempt_index,
                max_attempts=max_attempts,
                status_code=status_code,
                had_timeout=False,
                base_delay_s=0.5,
                max_delay_s=5.0,
            )
            results.append(
                {
                    'attempt': str(attempt_index),
                    'outcome': outcome,
                    'decision': decision.reason
                }
            )

        if not decision.should_retry:
            return results

        time.sleep(decision.delay_s)
        attempt_index += 1


if __name__ == '__main__':
    attempt_results = simulate_delivery(
        outcomes=['500', 'timeout', '500', '200'],
        max_attempts=5
    )
    for row in attempt_results:
        print(row)
