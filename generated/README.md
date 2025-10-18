# Bank Account Class

A simple Python implementation of a bank account with deposit, withdraw, and balance methods.

## Features

- **Deposit**: Add money to the account
- **Withdraw**: Remove money from the account (with insufficient funds check)
- **Balance**: Check the current account balance
- **Input Validation**: Proper error handling for negative amounts and insufficient funds

## Usage

```python
from bank_account import BankAccount

# Create an account with initial balance
account = BankAccount(1000.0)

# Deposit money
account.deposit(500.0)

# Withdraw money
account.withdraw(300.0)

# Check balance
current_balance = account.balance()
print(f"Current balance: ${current_balance}")
```

## Running Tests

```bash
pytest test_bank_account.py -v
```

## Code Quality

The code follows PEP 8 standards and passes:
- **flake8** (100% clean)
- **pylint** (10.00/10 rating)

All methods include:
- Type hints
- Comprehensive docstrings
- Input validation
- Error handling
