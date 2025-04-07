from langchain.tools import tool
import uuid
from datetime import datetime, timedelta
import json

@tool
def get_fee_charged_transactions(account_number: int) -> list:
    """
    Retrieves a list of fee-charged transactions for a given account in last year.

    Each transaction includes:
    - Transaction ID: Unique identifier for the transaction.
    - Transaction Date: Date when the fee was charged.
    - Transaction Amount: The amount of the fee charged.
    - Fee Type: Description of the type of fee applied.
    - Refund Status: Boolean - True if the fee charged has refunded already it menas it can not be refunded again. False if fee charged has not refunded and eligible for refund.

    Args:
        account_number (int): The unique identifier of the customer's account.
        account_number will come from user input.

    Returns:
        list: A fixed list of 5 dictionaries, each representing a fee-charged transaction.
    """
    transactions = [
        {
            "transaction-id": str(uuid.uuid4()),  
            "transaction-date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
            "transaction-amount": 25.00 +account_number%10,
            "fee-type": "Overdraft Fee",
            "refund-status": False
        },
        {
            "transaction-id": str(uuid.uuid4()),
            "transaction-date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "transaction-amount": 3.50+account_number%100,
            "fee-type": "ATM Withdrawal Fee",
            "refund-status": True
        },
        {
            "transaction-id": str(uuid.uuid4()),
            "transaction-date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
            "transaction-amount": 15.00+account_number%10,
            "fee-type": "Monthly Maintenance Fee",
            "refund-status": False
        },
        {
            "transaction-id": str(uuid.uuid4()),
            "transaction-date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
            "transaction-amount": 7.00+account_number%25,
            "fee-type": "Foreign Transaction Fee",
            "refund-status": True
        },
        {
            "transaction-id": str(uuid.uuid4()),
            "transaction-date": (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d"),
            "transaction-amount": 12.75+account_number%11,
            "fee-type": "Wire Transfer Fee",
            "refund-status": False
        }
    ]

    return json.dumps(transactions)
