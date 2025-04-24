from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial-tracker")

# Store transactions in memory for demo purposes
# In a real application, this would be a database
transactions: List[Dict[str, Any]] = []
categories: List[str] = ["Income", "Food", "Transportation", "Utilities", "Entertainment", "Other"]

@mcp.tool()
async def add_transaction(amount: float, category: str, description: str) -> str:
    """Add a new financial transaction.
    
    Args:
        amount: Transaction amount (positive for income, negative for expenses)
        category: Transaction category (e.g., "Food", "Transportation")
        description: Description of the transaction
    """
    if category not in categories:
        return f"Invalid category. Please use one of: {', '.join(categories)}"
    
    transaction = {
        "amount": amount,
        "category": category,
        "description": description
    }
    transactions.append(transaction)
    return f"Transaction added: {amount} ({category}) - {description}"

@mcp.tool()
async def get_balance() -> str:
    """Get current balance and summary of transactions."""
    if not transactions:
        return "No transactions recorded yet."
    
    total = sum(t["amount"] for t in transactions)
    by_category = {}
    for t in transactions:
        cat = t["category"]
        by_category[cat] = by_category.get(cat, 0) + t["amount"]
    
    summary = ["Current balance: ${:.2f}".format(total)]
    summary.append("\nBreakdown by category:")
    for cat, amount in by_category.items():
        summary.append(f"{cat}: ${amount:.2f}")
    
    return "\n".join(summary)

@mcp.tool()
async def list_transactions(category: str = None) -> str:
    """List all transactions, optionally filtered by category.
    
    Args:
        category: Optional category to filter transactions
    """
    if not transactions:
        return "No transactions recorded yet."
    
    filtered = transactions
    if category:
        if category not in categories:
            return f"Invalid category. Please use one of: {', '.join(categories)}"
        filtered = [t for t in transactions if t["category"] == category]
        if not filtered:
            return f"No transactions found in category: {category}"
    
    result = []
    for t in filtered:
        result.append(f"${t['amount']:.2f} ({t['category']}) - {t['description']}")
    
    return "\n".join(result)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')