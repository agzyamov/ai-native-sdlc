"""
Unit tests for the fibonacci module.

Tests both the memoized recursive implementation and the iterative
implementation of the Fibonacci sequence calculator.
"""

import unittest
from fibonacci import fibonacci, fibonacci_iterative


class TestFibonacci(unittest.TestCase):
    """Test cases for the fibonacci function with memoization."""

    def test_base_cases(self):
        """Test the base cases of the Fibonacci sequence."""
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_small_numbers(self):
        """Test Fibonacci numbers for small inputs."""
        self.assertEqual(fibonacci(2), 1)
        self.assertEqual(fibonacci(3), 2)
        self.assertEqual(fibonacci(4), 3)
        self.assertEqual(fibonacci(5), 5)
        self.assertEqual(fibonacci(6), 8)
        self.assertEqual(fibonacci(7), 13)

    def test_medium_numbers(self):
        """Test Fibonacci numbers for medium-sized inputs."""
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(15), 610)
        self.assertEqual(fibonacci(20), 6765)

    def test_float_input(self):
        """Test that float inputs are converted to integers."""
        self.assertEqual(fibonacci(5.0), 5)
        self.assertEqual(fibonacci(10.7), 55)

    def test_negative_input(self):
        """Test that negative inputs raise ValueError."""
        with self.assertRaises(ValueError):
            fibonacci(-1)
        with self.assertRaises(ValueError):
            fibonacci(-10)

    def test_invalid_input(self):
        """Test that invalid inputs raise TypeError."""
        with self.assertRaises(TypeError):
            fibonacci("invalid")
        with self.assertRaises(TypeError):
            fibonacci(None)
        with self.assertRaises(TypeError):
            fibonacci([1, 2, 3])


class TestFibonacciIterative(unittest.TestCase):
    """Test cases for the iterative fibonacci implementation."""

    def test_base_cases(self):
        """Test the base cases of the Fibonacci sequence."""
        self.assertEqual(fibonacci_iterative(0), 0)
        self.assertEqual(fibonacci_iterative(1), 1)

    def test_small_numbers(self):
        """Test Fibonacci numbers for small inputs."""
        self.assertEqual(fibonacci_iterative(2), 1)
        self.assertEqual(fibonacci_iterative(3), 2)
        self.assertEqual(fibonacci_iterative(4), 3)
        self.assertEqual(fibonacci_iterative(5), 5)
        self.assertEqual(fibonacci_iterative(6), 8)
        self.assertEqual(fibonacci_iterative(7), 13)

    def test_medium_numbers(self):
        """Test Fibonacci numbers for medium-sized inputs."""
        self.assertEqual(fibonacci_iterative(10), 55)
        self.assertEqual(fibonacci_iterative(15), 610)
        self.assertEqual(fibonacci_iterative(20), 6765)

    def test_consistency_with_memoized(self):
        """Test that both implementations produce the same results."""
        for i in range(25):
            self.assertEqual(
                fibonacci(i),
                fibonacci_iterative(i),
                f"Mismatch at n={i}"
            )

    def test_float_input(self):
        """Test that float inputs are converted to integers."""
        self.assertEqual(fibonacci_iterative(5.0), 5)
        self.assertEqual(fibonacci_iterative(10.7), 55)

    def test_negative_input(self):
        """Test that negative inputs raise ValueError."""
        with self.assertRaises(ValueError):
            fibonacci_iterative(-1)
        with self.assertRaises(ValueError):
            fibonacci_iterative(-10)

    def test_invalid_input(self):
        """Test that invalid inputs raise TypeError."""
        with self.assertRaises(TypeError):
            fibonacci_iterative("invalid")
        with self.assertRaises(TypeError):
            fibonacci_iterative(None)


if __name__ == '__main__':
    unittest.main()
