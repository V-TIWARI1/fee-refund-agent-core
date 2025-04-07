import random
import uuid
from datetime import datetime, timedelta

def get_customer_context() -> dict:
    """
    Fetches customer details for an active session.

    This function retrieves a legitimate customer's information who is currently in session 
    and is eligible to request a fee refund. The returned data includes:

    - Customer ID (Unique identifier for the customer)
    - Customer Name (Full name of the customer)
    - Customer Open Date (The date when the customer joined the bank)
    - SSN (Social Security Number associated with the customer)
    - Tax ID (Tax Identification Number associated with the customer)
    - Customer Session ID (A unique session identifier for the current transaction)

    Returns:
        dict: A dictionary containing the authenticated customer details.
    """
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller"]

    # Generate customer details
    customer_id = random.randint(100000, 999999)  # Unique customer ID
    customer_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Generate a customer open date (within the last 10 years)
    start_date = datetime.now() - timedelta(days=365 * 10)
    random_days = random.randint(0, 365 * 10)
    customer_open_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

    # Generate SSN and Tax ID
    ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    tax_id = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"

    # Generate a unique session ID
    customer_session_id = str(uuid.uuid4())

    return {
        "customer-id": customer_id,
        "customer-name": customer_name,
        "customer-open-date": customer_open_date,
        "ssn": ssn,
        "tax-id": tax_id,
        "customer-session-id": customer_session_id
    }