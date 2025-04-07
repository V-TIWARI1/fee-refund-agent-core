import random
from langchain.tools import tool

@tool
def submit_refund(transaction_ids: list) -> dict:
    """
    Processes refund requests for a list of fee transactions.

    This function takes a list of transaction IDs and attempts to process refunds 
    for each transaction. It returns a dictionary mapping each transaction ID 
    to a refund status, indicating whether the refund was successfully processed.

    **Refund Processing Logic:**
    - If a transaction is eligible for a refund, it will be processed.
    - If a transaction is not eligible, the refund request will be denied.

    Args:
        transaction_ids (list): A list of transaction IDs for which refunds are requested.
        transaction_ids will come from user input

    Returns:
        dict: A dictionary where:
              - Key: Transaction ID
              - Value: Boolean indicating refund status
                  - True: Refund was successfully processed.
                  - False: Refund request was denied.
    """
    refund_results = {}

    for transaction_id in transaction_ids:
        # Simulate refund eligibility check
        refund_success = random.choice([True, False])  # System determines refund eligibility

        refund_results[transaction_id] = refund_success

    return True
