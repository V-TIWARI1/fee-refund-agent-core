import random
from langchain.tools import tool

@tool
def submit_refund(transactions: list) -> dict:
    """
    Processes fee refund requests for a list of fee transactions with reasons.

    This function takes a list of transaction ID,
    It attempts to process refunds 
    and returns a boolean wether refund was usccessful or not.

    **Refund Processing Logic:**
    - If a transaction is eligible for a refund, it will be processed.
    - If a transaction is not eligible, the refund request will be denied.

    Args:
        transactions (list): list of transaction ids

    Returns:
        boolean weather refund was process successfully or not
    """
    refund_results = {}

    for transaction_id in transactions:
        # Simulate refund eligibility check
        refund_success = True 
        refund_results[transaction_id] = refund_success

    return True