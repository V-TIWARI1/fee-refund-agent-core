import random
from langchain.tools import tool

@tool
def submit_refund(transactions: dict) -> dict:
    """
    Processes fee refund requests for a list of fee transactions with reasons.

    This function takes a dictionary where each key is a transaction ID and the 
    value is the reason for requesting the refund. It attempts to process refunds 
    and returns a dictionary mapping each transaction ID to a refund status.

    **Refund Processing Logic:**
    - If a transaction is eligible for a refund, it will be processed.
    - If a transaction is not eligible, the refund request will be denied.

    Args:
        transactions (dict): A dictionary where:
            - Key: Transaction ID (str or int)
            - Value: Reason for refund (str)

    Returns:
        dict: A dictionary where:
              - Key: Transaction ID
              - Value: Boolean indicating refund status
                  - True: Refund was successfully processed.
                  - False: Refund request was denied.
    """
    refund_results = {}

    for transaction_id, reason in transactions.items():
        # Simulate refund eligibility check
        refund_success = True 
        refund_results[transaction_id] = refund_success

    return True