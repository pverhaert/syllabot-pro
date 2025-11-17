"""
Utility functions for handling LLM calls with retry logic and exponential backoff.
"""
import time
from typing import Callable, Any
from rich.console import Console

console = Console()


def kickoff_with_retry(
    crew_kickoff_func: Callable,
    inputs: dict,
    max_retries: int = 5,
    initial_delay: int = 2,
    max_delay: int = 60
) -> Any:
    """
    Execute crew.kickoff() with exponential backoff retry logic for handling overloaded models.

    Args:
        crew_kickoff_func: The crew.kickoff function to call
        inputs: Input dictionary to pass to kickoff
        max_retries: Maximum number of retry attempts (default: 5)
        initial_delay: Initial delay in seconds before first retry (default: 2)
        max_delay: Maximum delay in seconds between retries (default: 60)

    Returns:
        The result from crew.kickoff()

    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            result = crew_kickoff_func(inputs=inputs)
            return result

        except Exception as e:
            error_str = str(e).lower()

            # Check if it's a retriable error (503, overloaded, unavailable)
            is_retriable = any(indicator in error_str for indicator in [
                "503",
                "unavailable",
                "overloaded",
                "rate limit",
                "quota exceeded",
                "too many requests"
            ])

            # If it's the last attempt or not a retriable error, raise the exception
            if attempt == max_retries - 1 or not is_retriable:
                console.print(f"\n❌ Failed after {attempt + 1} attempts: {str(e)}\n", style="bold red")
                raise

            # Calculate delay with exponential backoff (capped at max_delay)
            delay = min(initial_delay * (2 ** attempt), max_delay)

            console.print(
                f"\n⚠️  Model overloaded or unavailable (Attempt {attempt + 1}/{max_retries})",
                style="yellow"
            )
            console.print(f"   Error: {str(e)[:200]}", style="dim yellow")
            console.print(f"   Retrying in {delay} seconds...\n", style="yellow")

            time.sleep(delay)

    raise Exception(f"Failed after {max_retries} retry attempts")

