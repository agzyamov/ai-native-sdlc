"""Unit tests for the BankAccount class."""

import pytest
from bank_account import BankAccount


def test_initial_balance_default():
    """Test creating account with default initial balance."""
    account = BankAccount()
    assert account.balance() == 0.0


def test_initial_balance_custom():
    """Test creating account with custom initial balance."""
    account = BankAccount(100.0)
    assert account.balance() == 100.0


def test_initial_balance_negative():
    """Test that negative initial balance raises ValueError."""
    with pytest.raises(ValueError, match="Initial balance cannot be negative"):
        BankAccount(-50.0)


def test_deposit_positive_amount():
    """Test depositing a positive amount."""
    account = BankAccount(100.0)
    account.deposit(50.0)
    assert account.balance() == 150.0


def test_deposit_multiple_times():
    """Test multiple deposits."""
    account = BankAccount()
    account.deposit(100.0)
    account.deposit(50.0)
    account.deposit(25.0)
    assert account.balance() == 175.0


def test_deposit_zero_amount():
    """Test that depositing zero raises ValueError."""
    account = BankAccount()
    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        account.deposit(0)


def test_deposit_negative_amount():
    """Test that depositing negative amount raises ValueError."""
    account = BankAccount()
    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        account.deposit(-50.0)


def test_withdraw_positive_amount():
    """Test withdrawing a positive amount."""
    account = BankAccount(100.0)
    account.withdraw(30.0)
    assert account.balance() == 70.0


def test_withdraw_entire_balance():
    """Test withdrawing the entire balance."""
    account = BankAccount(100.0)
    account.withdraw(100.0)
    assert account.balance() == 0.0


def test_withdraw_insufficient_funds():
    """Test that withdrawing more than balance raises ValueError."""
    account = BankAccount(50.0)
    with pytest.raises(ValueError, match="Insufficient funds"):
        account.withdraw(100.0)


def test_withdraw_zero_amount():
    """Test that withdrawing zero raises ValueError."""
    account = BankAccount(100.0)
    with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
        account.withdraw(0)


def test_withdraw_negative_amount():
    """Test that withdrawing negative amount raises ValueError."""
    account = BankAccount(100.0)
    with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
        account.withdraw(-30.0)


def test_deposit_and_withdraw_sequence():
    """Test a sequence of deposits and withdrawals."""
    account = BankAccount(100.0)
    account.deposit(50.0)
    assert account.balance() == 150.0
    account.withdraw(30.0)
    assert account.balance() == 120.0
    account.deposit(20.0)
    assert account.balance() == 140.0
    account.withdraw(40.0)
    assert account.balance() == 100.0
