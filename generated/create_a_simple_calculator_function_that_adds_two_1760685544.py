"""
Calculator module for basic arithmetic operations.
"""


def add(a, b):
"""
Add two numbers together.

Args:
a: First number (int, float, or numeric type)
b: Second number (int, float, or numeric type)

Returns:
The sum of a and b

Raises:
TypeError: If either argument is not a number
ValueError: If either argument is None

Examples:
>>> add(2, 3)
5
>>> add(2.5, 3.7)
6.2
>>> add(-1, 1)
0
"""
# Validate inputs
if a is None or b is None:
raise ValueError("Arguments cannot be None")

# Check if inputs are numeric
if not isinstance(a, (int, float, complex)) or isinstance(a, bool):
raise TypeError(f"First argument must be a number, got {type(a).__name__}")

if not isinstance(b, (int, float, complex)) or isinstance(b, bool):
raise TypeError(f"Second argument must be a number, got {type(b).__name__}")

# Perform addition
return a + b


# Unit tests
if __name__ == "__main__":
import unittest

class TestAddFunction(unittest.TestCase):
"""Test cases for the add function."""

def test_add_positive_integers(self):
"""Test adding two positive integers."""
self.assertEqual(add(2, 3), 5)
self.assertEqual(add(10, 20), 30)

def test_add_negative_integers(self):
"""Test adding negative integers."""
self.assertEqual(add(-5, -3), -8)
self.assertEqual(add(-10, 5), -5)

def test_add_floats(self):
"""Test adding floating point numbers."""
self.assertAlmostEqual(add(2.5, 3.7), 6.2)
self.assertAlmostEqual(add(1.1, 2.2), 3.3)

def test_add_mixed_types(self):
"""Test adding integers and floats."""
self.assertEqual(add(5, 2.5), 7.5)
self.assertEqual(add(3.5, 2), 5.5)

def test_add_zero(self):
"""Test adding zero."""
self.assertEqual(add(0, 5), 5)
self.assertEqual(add(5, 0), 5)
self.assertEqual(add(0, 0), 0)

def test_add_complex_numbers(self):
"""Test adding complex numbers."""
self.assertEqual(add(1+2j, 3+4j), 4+6j)

def test_add_with_none(self):
"""Test that None values raise ValueError."""
with self.assertRaises(ValueError):
add(None, 5)
with self.assertRaises(ValueError):
add(5, None)

def test_add_with_invalid_types(self):
"""Test that invalid types raise TypeError."""
with self.assertRaises(TypeError):
add("5", 3)
with self.assertRaises(TypeError):
add(5, "3")
with self.assertRaises(TypeError):
add([1, 2], 3)
with self.assertRaises(TypeError):
add(True, 5)  # Booleans are not allowed

# Run tests
unittest.main(verbosity=2)
