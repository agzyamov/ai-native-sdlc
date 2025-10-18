"""
Unit tests for the factorial module.

This module contains comprehensive tests for the factorial function.
"""

import unittest
from factorial import factorial


class TestFactorial(unittest.TestCase):
    """Test cases for the factorial function."""

    def test_factorial_zero(self):
        """Test factorial of 0 equals 1."""
        self.assertEqual(factorial(0), 1)

    def test_factorial_one(self):
        """Test factorial of 1 equals 1."""
        self.assertEqual(factorial(1), 1)

    def test_factorial_small_numbers(self):
        """Test factorial of small positive integers."""
        self.assertEqual(factorial(2), 2)
        self.assertEqual(factorial(3), 6)
        self.assertEqual(factorial(4), 24)
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(6), 720)

    def test_factorial_larger_numbers(self):
        """Test factorial of larger positive integers."""
        self.assertEqual(factorial(10), 3628800)
        self.assertEqual(factorial(15), 1307674368000)
        self.assertEqual(factorial(20), 2432902008176640000)

    def test_factorial_negative_raises_value_error(self):
        """Test that negative numbers raise ValueError."""
        with self.assertRaises(ValueError) as context:
            factorial(-1)
        self.assertIn('non-negative', str(context.exception))

        with self.assertRaises(ValueError):
            factorial(-5)

        with self.assertRaises(ValueError):
            factorial(-100)

    def test_factorial_non_integer_raises_type_error(self):
        """Test that non-integer inputs raise TypeError."""
        with self.assertRaises(TypeError) as context:
            factorial(3.5)
        self.assertIn('must be an integer', str(context.exception))

        with self.assertRaises(TypeError):
            factorial('5')

        with self.assertRaises(TypeError):
            factorial([5])

        with self.assertRaises(TypeError):
            factorial(None)


if __name__ == '__main__':
    unittest.main()
