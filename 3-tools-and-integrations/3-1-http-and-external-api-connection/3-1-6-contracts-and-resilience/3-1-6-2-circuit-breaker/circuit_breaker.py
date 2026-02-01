import random
import time
from typing import Any, Callable


class CircuitBreaker:
    def __init__(self, fail_threshold: int, reset_timeout: float) -> None:
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.state = 'closed'
        self.last_fail_time = 0.0

    def check_allowed(self, current_time: float) -> bool:
        """Check whether a call is allowed based on breaker state.
        Args:
            current_time (float): Current time in seconds from time.time()."""
        if self.state != 'open':
            return True

        if current_time - self.last_fail_time >= self.reset_timeout:
            self.state = 'half-open'
            return True

        return False

    def record_failure(self, current_time: float) -> None:
        """Record a failed call and possibly open the breaker.
        Args:
            current_time (float): Current time in seconds from time.time()."""
        self.fail_count += 1
        self.last_fail_time = current_time

        if self.fail_count >= self.fail_threshold:
            self.state = 'open'

    def record_success(self) -> None:
        """Record a successful call and close/reset the breaker.
        Args:
            None: No arguments."""
        self.fail_count = 0
        self.state = 'closed'

    def wrap_call(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap a callable with circuit breaker protection.
        Args:
            func (Callable[..., Any]): Target callable to protect."""
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_time = time.time()

            if not self.check_allowed(current_time=current_time):
                raise RuntimeError(
                    'Circuit breaker OPEN — external API temporarily disabled')

            try:
                result = func(*args, **kwargs)

                if self.state == 'half-open':
                    self.record_success()
                elif self.state == 'closed':
                    self.fail_count = 0

                return result
            except (TimeoutError, ConnectionError):
                self.record_failure(current_time=current_time)
                raise

        return wrapper


def build_breaker(fail_threshold: int, reset_timeout: float) -> CircuitBreaker:
    """Build a circuit breaker instance.
    Args:
        fail_threshold (int): Number of failures to open the breaker.
        reset_timeout (float): Cooldown time in seconds before half-open."""
    breaker = CircuitBreaker(
        fail_threshold=fail_threshold, reset_timeout=reset_timeout)
    return breaker


def call_external_api(user_id: int, fail_rate: float) -> dict[str, Any]:
    """Simulate an external API call that may fail.
    Args:
        user_id (int): User identifier to request.
        fail_rate (float): Probability of transport failure (0..1)."""
    if random.random() < fail_rate:
        raise ConnectionError('Simulated connection error')

    payload = {'id': user_id, 'email': 'user@example.com'}
    return payload


def run_call_series(
        call_count: int, fail_rate: float, sleep_seconds: float) -> list[str]:
    """Run a series of protected calls and collect outcomes.
    Args:
        call_count (int): Number of calls to execute.
        fail_rate (float): Probability of transport failure (0..1).
        sleep_seconds (float): Delay between calls in seconds."""
    breaker = build_breaker(fail_threshold=2, reset_timeout=3.0)
    protected_call = breaker.wrap_call(call_external_api)

    outcomes: list[str] = []

    for index in range(call_count):
        try:
            data = protected_call(user_id=1, fail_rate=fail_rate)
            outcomes.append(f'#{index}: ok state={breaker.state} data={data}')
        except Exception as exc:
            outcomes.append(
                f'#{index}: error state={breaker.state} error={exc}')

        time.sleep(sleep_seconds)

    return outcomes


if __name__ == '__main__':
    outcomes = run_call_series(call_count=8, fail_rate=0.7, sleep_seconds=1.0)

    for line in outcomes:
        print(line)
