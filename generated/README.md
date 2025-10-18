# Palindrome Checker

A simple Python function to check if a string is a palindrome.

## Features

- **Case-insensitive**: Treats uppercase and lowercase letters the same
- **Ignores punctuation and spaces**: Only considers alphanumeric characters
- **Comprehensive**: Handles edge cases like empty strings and single characters
- **Well-tested**: Includes 10 unit tests covering various scenarios
- **PEP 8 compliant**: Follows Python style guidelines with type hints and docstrings

## Usage

```python
from palindrome_checker import is_palindrome

# Simple palindromes
print(is_palindrome('racecar'))  # True
print(is_palindrome('hello'))    # False

# Case-insensitive
print(is_palindrome('RaceCar'))  # True

# Ignores spaces and punctuation
print(is_palindrome('A man a plan a canal Panama'))  # True
print(is_palindrome('Was it a car or a cat I saw?'))  # True

# Edge cases
print(is_palindrome(''))   # True (empty string)
print(is_palindrome('a'))  # True (single character)
```

## Running Tests

```bash
# Run all tests
pytest test_palindrome_checker.py -v

# Run with coverage
pytest test_palindrome_checker.py --cov=palindrome_checker
```

## Linting

The code passes both flake8 and pylint with perfect scores:

```bash
# Check with flake8
flake8 --max-line-length=100 palindrome_checker.py

# Check with pylint
pylint --max-line-length=100 palindrome_checker.py
```

## Implementation Details

The `is_palindrome()` function works by:
1. Removing all non-alphanumeric characters from the input string
2. Converting the remaining characters to lowercase
3. Comparing the cleaned string with its reverse

This approach ensures that the function correctly identifies palindromes regardless of:
- Letter casing
- Spaces
- Punctuation marks
- Special characters

## Test Coverage

The test suite includes 10 comprehensive test cases:
- ✓ Simple single-word palindromes
- ✓ Non-palindrome strings
- ✓ Case-insensitive checking
- ✓ Strings with spaces
- ✓ Strings with punctuation
- ✓ Empty strings
- ✓ Single characters
- ✓ Numeric strings
- ✓ Mixed alphanumeric strings
- ✓ Strings with only spaces and punctuation
