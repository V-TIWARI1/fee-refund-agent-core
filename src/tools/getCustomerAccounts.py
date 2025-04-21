from langchain.tools import tool
import json

@tool
def get_customer_accounts(customer_id: int) -> list:
    """
    Fetches the list of bank accounts associated with a given customer only for fee refund context.

    Args:
        customer_id (int): The unique identifier for the customer.

    Returns:
        list: A list of 5 dictionaries, each representing an account.
    """
    accounts = [
        {
            "account-number": 1000123456,
            "account-type": "Checking",
            "product-code": "1001",
            "subproduct-code": 101,
            "product-type": "Basic Checking",
            "account-balance": 2500.75
        },
        {
            "account-number": 1000234567,
            "account-type": "Savings",
            "product-code": "1002",
            "subproduct-code": 202,
            "product-type": "High-Yield Savings",
            "account-balance": 15000.50
        },
        {
            "account-number": 1000345678,
            "account-type": "Credit Card",
            "product-code": "1001",
            "subproduct-code": 303,
            "product-type": "Rewards Credit Card",
            "account-balance": -200.00  # Negative balance represents credit usage
        },
        {
            "account-number": 1000456789,
            "account-type": "Checking",
            "product-code": "1001",
            "subproduct-code": 404,
            "product-type": "Premium Checking",
            "account-balance": 7800.00
        },
        {
            "account-number": 1000567890,
            "account-type": "Savings",
            "product-code": "1002",
            "subproduct-code": 505,
            "product-type": "Basic Savings",
            "account-balance": 500.25
        }
    ]

    return json.dumps(accounts)
