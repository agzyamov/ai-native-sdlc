"""
Factorial calculation module.

This module provides a simple function to calculate the factorial of a number.
"""


def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer.

    The factorial of n (denoted as n!) is the product of all positive integers
    less than or equal to n. By definition, 0! = 1.

    Args:
        n: A non-negative integer for which to calculate the factorial.

    Returns:
        The factorial of n as an integer.

    Raises:
        TypeError: If n is not an integer.
        ValueError: If n is negative.

    Examples:
        >>> factorial(0)
        1
        >>> factorial(1)
        1
        >>> factorial(5)
        120
        >>> factorial(10)
        3628800
    """
    if not isinstance(n, int):
        raise TypeError(f'n must be an integer, got {type(n).__name__}')

    if n < 0:
        raise ValueError(f'n must be non-negative, got {n}')

    if n in (0, 1):
        return 1

    result = 1
    for i in range(2, n + 1):
        result *= i

    return result
