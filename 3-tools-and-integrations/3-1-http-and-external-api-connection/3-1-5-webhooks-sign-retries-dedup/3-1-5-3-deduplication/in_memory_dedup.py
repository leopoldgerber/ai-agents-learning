from typing import Any


processed_event_ids: set[str] = set()


def is_duplicate_event(event_id: str) -> bool:
    """Check whether event was already processed.
    Args:
        event_id (str): Unique event identifier."""
    return event_id in processed_event_ids


def mark_event_processed(event_id: str) -> None:
    """Mark event as processed in memory.
    Args:
        event_id (str): Unique event identifier."""
    processed_event_ids.add(event_id)


def handle_event(event_id: str, payload: dict[str, Any]) -> str:
    """Handle incoming event with in-memory deduplication.
    Args:
        event_id (str): Unique event identifier.
        payload (dict[str, Any]): Event payload."""
    if is_duplicate_event(event_id=event_id):
        return 'duplicate'

    mark_event_processed(event_id=event_id)

    # business logic (simulated)
    _ = payload

    return 'processed'


if __name__ == '__main__':
    result_1 = handle_event(event_id='evt_1', payload={'type': 'invoice.paid'})
    result_2 = handle_event(event_id='evt_1', payload={'type': 'invoice.paid'})

    print(result_1)
    print(result_2)
