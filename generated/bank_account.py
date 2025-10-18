"""Simple bank account implementation with deposit, withdraw, and balance methods."""


class BankAccount:
    """A simple bank account class for managing deposits and withdrawals."""

    def __init__(self, initial_balance: float = 0.0) -> None:
        """
        Initialize a bank account with an optional initial balance.

        Args:
            initial_balance: The starting balance for the account (default: 0.0)

        Raises:
            ValueError: If initial_balance is negative
        """
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._balance = initial_balance

    def deposit(self, amount: float) -> None:
        """
        Deposit money into the account.

        Args:
            amount: The amount to deposit

        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        """
        Withdraw money from the account.

        Args:
            amount: The amount to withdraw

        Raises:
            ValueError: If amount is not positive or exceeds balance
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount

    def balance(self) -> float:
        """
        Get the current account balance.

        Returns:
            The current balance
        """
        return self._balance
