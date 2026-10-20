from app.services.loan_service import (
    get_outstanding_balance,
    get_emi_details,
    get_payment_history,
)


def test_outstanding_balance():

    result = get_outstanding_balance("C001")

    assert result["success"] is True
    assert result["loan_count"] == 2

    assert result["total_outstanding_amount"] == 255000

    print("\nOutstanding balance:", result)


def test_emi_details():

    result = get_emi_details("C001")

    assert result["success"] is True
    assert len(result["emi_details"]) == 2

    print("\nEMI details:", result)


def test_payment_history():

    result = get_payment_history("C001")

    assert result["success"] is True
    assert len(result["payments"]) == 3

    print("\nPayment history:", result)


def test_unknown_customer():

    result = get_outstanding_balance("UNKNOWN")

    assert result["success"] is False


def test_invalid_limit():

    result = get_payment_history("C001", limit=100)

    assert result["success"] is False