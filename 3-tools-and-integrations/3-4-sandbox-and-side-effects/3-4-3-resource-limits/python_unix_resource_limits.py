import resource
import signal
import sys


def set_limits() -> None:
    """Set CPU and memory limits for current process."""

    # Limit address space to 256 MB
    memory_limit = 256 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

    # Limit CPU time to 5 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))


def handle_timeout(signum, frame):
    print("CPU time limit exceeded")
    sys.exit(1)


def main() -> None:
    signal.signal(signal.SIGXCPU, handle_timeout)

    set_limits()

    # Simulate heavy memory usage
    data = []
    while True:
        data.append("x" * 10_000_000)


if __name__ == "__main__":
    main()
