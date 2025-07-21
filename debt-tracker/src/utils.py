def validate_amount(amount):
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return True

def format_debt_record(debt):
    return f"Debt: {debt['amount']} - Description: {debt['description']}"

def calculate_total_debt(debts):
    return sum(debt['amount'] for debt in debts)