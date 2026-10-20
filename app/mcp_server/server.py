from mcp.server.fastmcp import FastMCP

from app.services.loan_service import (
    get_outstanding_balance,
    get_emi_details,
    get_payment_history,
)


# Create the MCP server
mcp = FastMCP("NBFC Loan Service")


@mcp.tool()
def outstanding_balance(customer_id: str) -> dict:
    """
    Retrieve the outstanding balances for a customer.

    Args:
        customer_id: Customer identifier in the development dataset.
    """
    return get_outstanding_balance(customer_id)

@mcp.tool()
def emi_details(customer_id: str) -> dict:
    """
    Retrieve EMI amounts and upcoming EMI dates for a customer.

    Args:
        customer_id: Customer identifier in the development dataset.
    """
    return get_emi_details(customer_id)

@mcp.tool()
def payment_history(customer_id: str, limit: int = 5) -> dict:
    """
    Retrieve recent payment history for a customer.

    Args:
        customer_id: Customer identifier in the development dataset.
        limit: Maximum number of payment records to retrieve.
    """
    return get_payment_history(customer_id, limit)


if __name__ == "__main__":
    mcp.run()