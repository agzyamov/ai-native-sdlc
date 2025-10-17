#!/usr/bin/env python3
"""
Prime Number Checker

A production-ready module for checking if a number is prime.
"""

import math
from typing import Union


def is_prime(n: Union[int, float]) -> bool:
"""
Check if a number is prime.

A prime number is a natural number greater than 1 that has no positive
divisors other than 1 and itself.

Args:
n: The number to check. Can be int or float (will be converted to int).

Returns:
bool: True if the number is prime, False otherwise.

Raises:
TypeError: If n cannot be converted to an integer.
ValueError: If n is negative.

Examples:
>>> is_prime(2)
True
>>> is_prime(17)
True
>>> is_prime(4)
False
>>> is_prime(1)
False
"""
# Type checking and conversion
try:
if isinstance(n, float):
if not n.is_integer():
return False
n = int(n)
elif not isinstance(n, int):
n = int(n)
except (ValueError, TypeError) as e:
raise TypeError(f"Cannot convert {n} to integer: {e}")

# Validation
if n < 0:
raise ValueError("Prime check is only defined for non-negative integers")

# Handle edge cases
if n <= 1:
return False
if n == 2:
return True
if n % 2 == 0:
return False

# Check odd divisors up to sqrt(n)
# This is the most efficient algorithm for single prime checks
sqrt_n = int(math.sqrt(n))
for i in range(3, sqrt_n + 1, 2):
if n % i == 0:
return False

return True


def find_primes_in_range(start: int, end: int) -> list[int]:
"""
Find all prime numbers in a given range [start, end].

Args:
start: The starting number (inclusive).
end: The ending number (inclusive).

Returns:
list[int]: A list of all prime numbers in the range.

Raises:
ValueError: If start or end is negative, or if start > end.

Examples:
>>> find_primes_in_range(1, 10)
[2, 3, 5, 7]
>>> find_primes_in_range(10, 20)
[11, 13, 17, 19]
"""
if start < 0 or end < 0:
raise ValueError("Range bounds must be non-negative")
if start > end:
raise ValueError("Start must be less than or equal to end")

return [n for n in range(start, end + 1) if is_prime(n)]


# Test suite
if __name__ == "__main__":
import unittest

class TestIsPrime(unittest.TestCase):
"""Test cases for the is_prime function."""

def test_small_primes(self):
"""Test small prime numbers."""
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
for p in primes:
self.assertTrue(is_prime(p), f"{p} should be prime")

def test_small_non_primes(self):
"""Test small non-prime numbers."""
non_primes = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
for n in non_primes:
self.assertFalse(is_prime(n), f"{n} should not be prime")

def test_edge_cases(self):
"""Test edge cases."""
self.assertFalse(is_prime(0), "0 is not prime")
self.assertFalse(is_prime(1), "1 is not prime")
self.assertTrue(is_prime(2), "2 is prime")

def test_large_primes(self):
"""Test large prime numbers."""
large_primes = [97, 101, 103, 107, 109, 1009, 10007]
for p in large_primes:
self.assertTrue(is_prime(p), f"{p} should be prime")

def test_large_non_primes(self):
"""Test large non-prime numbers."""
self.assertFalse(is_prime(1000), "1000 is not prime")
self.assertFalse(is_prime(10000), "10000 is not prime")

def test_float_inputs(self):
"""Test float inputs."""
self.assertTrue(is_prime(7.0), "7.0 should be prime")
self.assertFalse(is_prime(7.5), "7.5 should not be prime")
self.assertFalse(is_prime(8.0), "8.0 should not be prime")

def test_negative_numbers(self):
"""Test that negative numbers raise ValueError."""
with self.assertRaises(ValueError):
is_prime(-5)

def test_invalid_types(self):
"""Test that invalid types raise TypeError."""
with self.assertRaises(TypeError):
is_prime("not a number")
with self.assertRaises(TypeError):
is_prime(None)

class TestFindPrimesInRange(unittest.TestCase):
"""Test cases for the find_primes_in_range function."""

def test_basic_range(self):
"""Test finding primes in a basic range."""
result = find_primes_in_range(1, 10)
expected = [2, 3, 5, 7]
self.assertEqual(result, expected)

def test_range_with_no_primes(self):
"""Test range containing no primes."""
result = find_primes_in_range(24, 28)
self.assertEqual(result, [])

def test_single_number_range(self):
"""Test range with a single number."""
self.assertEqual(find_primes_in_range(7, 7), [7])
self.assertEqual(find_primes_in_range(8, 8), [])

def test_invalid_range(self):
"""Test invalid range bounds."""
with self.assertRaises(ValueError):
find_primes_in_range(10, 5)
with self.assertRaises(ValueError):
find_primes_in_range(-1, 10)

# Run tests
print("Running tests...\n")
unittest.main(verbosity=2)
