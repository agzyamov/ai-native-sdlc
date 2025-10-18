# Fibonacci Calculator with Memoization

This module provides an efficient implementation of the Fibonacci sequence calculator using memoization.

## Features

- **Memoized Recursive Implementation**: Uses `functools.lru_cache` for efficient memoization
- **Iterative Implementation**: Alternative implementation without recursion
- **Type Hints**: Full type annotation for better IDE support
- **Error Handling**: Proper validation and error messages
- **Comprehensive Tests**: Full test coverage with unittest
- **PEP 8 Compliant**: Passes flake8 and pylint with 10/10 rating

## Usage

### Basic Usage

```python
from fibonacci import fibonacci, fibonacci_iterative

# Calculate the 10th Fibonacci number (with memoization)
result = fibonacci(10)  # Returns: 55

# Using the iterative approach
result = fibonacci_iterative(10)  # Returns: 55
```

### Running the Module

```bash
python3 fibonacci.py
```

This will display the first 15 Fibonacci numbers calculated with both implementations.

### Running Tests

```bash
python3 -m unittest test_fibonacci.py -v
```

## Function Documentation

### `fibonacci(n)`

Calculate the nth Fibonacci number using memoization.

**Parameters:**
- `n` (int|float): The position in the Fibonacci sequence (0-indexed)

**Returns:**
- `int`: The nth Fibonacci number

**Raises:**
- `TypeError`: If n cannot be converted to an integer
- `ValueError`: If n is negative

**Time Complexity:** O(n) with memoization
**Space Complexity:** O(n) for the cache

### `fibonacci_iterative(n)`

Calculate the nth Fibonacci number using an iterative approach.

**Parameters:**
- `n` (int|float): The position in the Fibonacci sequence (0-indexed)

**Returns:**
- `int`: The nth Fibonacci number

**Raises:**
- `TypeError`: If n cannot be converted to an integer
- `ValueError`: If n is negative

**Time Complexity:** O(n)
**Space Complexity:** O(1)

## Examples

```python
# Base cases
fibonacci(0)  # 0
fibonacci(1)  # 1

# Small numbers
fibonacci(5)  # 5
fibonacci(10)  # 55

# Larger numbers (memoization makes this efficient)
fibonacci(20)  # 6765
fibonacci(30)  # 832040

# Float inputs are automatically converted
fibonacci(10.7)  # 55 (converted to 10)
```

## Code Quality

The code has been validated with:
- **flake8**: No issues (max-line-length=100)
- **pylint**: 10.00/10 rating
- **unittest**: 13 tests, all passing

## Implementation Details

The memoized version uses Python's `functools.lru_cache` decorator, which automatically caches function results based on input arguments. This reduces the time complexity from O(2^n) for naive recursion to O(n).

The iterative version avoids recursion entirely, making it suitable for very large values of n where stack overflow might be a concern.
