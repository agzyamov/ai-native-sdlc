"""
Fibonacci number calculator with memoization.

This module provides a function to calculate Fibonacci numbers efficiently
using memoization to avoid redundant calculations.
"""

from functools import lru_cache
from typing import Union


@lru_cache(maxsize=None)
def fibonacci(n: Union[int, float]) -> int:
    """
    Calculate the nth Fibonacci number using memoization.

    The Fibonacci sequence is defined as:
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2) for n > 1

    Uses the functools.lru_cache decorator to memoize results,
    providing O(n) time complexity instead of O(2^n).

    Args:
        n: The position in the Fibonacci sequence (0-indexed).
           Can be int or float, but will be converted to int.

    Returns:
        int: The nth Fibonacci number.

    Raises:
        TypeError: If n cannot be converted to an integer.
        ValueError: If n is negative.

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
        >>> fibonacci(20)
        6765
    """
    try:
        n = int(n)
    except (ValueError, TypeError) as e:
        raise TypeError(
            f"n must be an integer or convertible to int: {e}"
        ) from e

    if n < 0:
        raise ValueError("n must be a non-negative integer")

    if n <= 1:
        return n

    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_iterative(n: Union[int, float]) -> int:
    """
    Calculate the nth Fibonacci number using an iterative approach.

    This is an alternative implementation that doesn't use recursion,
    which can be useful for very large values of n to avoid stack overflow.

    Args:
        n: The position in the Fibonacci sequence (0-indexed).
           Can be int or float, but will be converted to int.

    Returns:
        int: The nth Fibonacci number.

    Raises:
        TypeError: If n cannot be converted to an integer.
        ValueError: If n is negative.

    Examples:
        >>> fibonacci_iterative(0)
        0
        >>> fibonacci_iterative(1)
        1
        >>> fibonacci_iterative(10)
        55
    """
    try:
        n = int(n)
    except (ValueError, TypeError) as e:
        raise TypeError(
            f"n must be an integer or convertible to int: {e}"
        ) from e

    if n < 0:
        raise ValueError("n must be a non-negative integer")

    if n <= 1:
        return n

    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr


if __name__ == '__main__':
    # Example usage
    print("Fibonacci numbers (with memoization):")
    for i in range(15):
        print(f"fibonacci({i}) = {fibonacci(i)}")

    print("\nFibonacci numbers (iterative):")
    for i in range(15):
        print(f"fibonacci_iterative({i}) = {fibonacci_iterative(i)}")
