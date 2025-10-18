"""Unit tests for palindrome checker module."""

from palindrome_checker import is_palindrome


class TestIsPalindrome:
    """Test cases for is_palindrome function."""

    def test_simple_palindrome(self):
        """Test simple single-word palindromes."""
        assert is_palindrome('racecar') is True
        assert is_palindrome('level') is True
        assert is_palindrome('noon') is True
        assert is_palindrome('madam') is True

    def test_non_palindrome(self):
        """Test non-palindrome strings."""
        assert is_palindrome('hello') is False
        assert is_palindrome('world') is False
        assert is_palindrome('python') is False

    def test_case_insensitive(self):
        """Test that palindrome check is case-insensitive."""
        assert is_palindrome('RaceCar') is True
        assert is_palindrome('Level') is True
        assert is_palindrome('NOON') is True

    def test_with_spaces(self):
        """Test palindromes with spaces."""
        assert is_palindrome('race car') is True
        assert is_palindrome('A man a plan a canal Panama') is True
        assert is_palindrome('never odd or even') is True

    def test_with_punctuation(self):
        """Test palindromes with punctuation."""
        assert is_palindrome('A man, a plan, a canal: Panama') is True
        assert is_palindrome('Was it a car or a cat I saw?') is True
        assert is_palindrome("Madam, I'm Adam") is True

    def test_empty_string(self):
        """Test empty string is considered a palindrome."""
        assert is_palindrome('') is True

    def test_single_character(self):
        """Test single character strings."""
        assert is_palindrome('a') is True
        assert is_palindrome('Z') is True
        assert is_palindrome('5') is True

    def test_numeric_strings(self):
        """Test palindromic numbers."""
        assert is_palindrome('12321') is True
        assert is_palindrome('12345') is False

    def test_mixed_alphanumeric(self):
        """Test strings with mixed letters and numbers."""
        assert is_palindrome('A1B2C2B1A') is True
        assert is_palindrome('test123test') is False

    def test_only_spaces_and_punctuation(self):
        """Test strings with only spaces and punctuation."""
        assert is_palindrome('   ') is True
        assert is_palindrome('!!!') is True
        assert is_palindrome('., .,') is True
