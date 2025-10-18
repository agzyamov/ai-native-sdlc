"""Palindrome checker module."""


def is_palindrome(text: str) -> bool:
    """
    Check if a string is a palindrome.

    A palindrome is a word, phrase, number, or other sequence of characters
    that reads the same forward and backward, ignoring spaces, punctuation,
    and capitalization.

    Args:
        text: The string to check for palindrome property.

    Returns:
        bool: True if the string is a palindrome, False otherwise.

    Examples:
        >>> is_palindrome('racecar')
        True
        >>> is_palindrome('hello')
        False
        >>> is_palindrome('A man a plan a canal Panama')
        True
        >>> is_palindrome('')
        True
    """
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned = ''.join(char.lower() for char in text if char.isalnum())

    # Check if the cleaned string is equal to its reverse
    return cleaned == cleaned[::-1]
