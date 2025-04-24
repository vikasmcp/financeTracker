from typing import Any, Dict, List
import sqlite3
import os
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial-tracker")

# Database setup
DB_FILE = "finance_tracker.db"

def initialize_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create transactions table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create categories table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Insert default categories if they don't exist
    default_categories = ["Income", "Food", "Transportation", "Utilities", "Entertainment", "Other"]
    for category in default_categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    
    conn.commit()
    conn.close()

def get_categories() -> List[str]:
    """Get all available transaction categories."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

@mcp.tool()
async def add_transaction(amount: float, category: str, description: str) -> str:
    """Add a new financial transaction.
    
    Args:
        amount: Transaction amount (positive for income, negative for expenses)
        category: Transaction category (e.g., "Food", "Transportation")
        description: Description of the transaction
    """
    categories = get_categories()
    if category not in categories:
        return f"Invalid category. Please use one of: {', '.join(categories)}"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (amount, category, description) VALUES (?, ?, ?)",
        (amount, category, description)
    )
    conn.commit()
    conn.close()
    
    return f"Transaction added: {amount} ({category}) - {description}"

@mcp.tool()
async def get_balance() -> str:
    """Get current balance and summary of transactions."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get total balance
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
    total = cursor.fetchone()[0]
    
    # Get breakdown by category
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    by_category = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    if not by_category:
        return "No transactions recorded yet."
    
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if category:
        categories = get_categories()
        if category not in categories:
            return f"Invalid category. Please use one of: {', '.join(categories)}"
        
        cursor.execute(
            "SELECT amount, category, description FROM transactions WHERE category = ? ORDER BY timestamp DESC",
            (category,)
        )
    else:
        cursor.execute("SELECT amount, category, description FROM transactions ORDER BY timestamp DESC")
    
    transactions = cursor.fetchall()
    conn.close()
    
    if not transactions:
        return "No transactions found." if category else "No transactions recorded yet."
    
    result = []
    for t in transactions:
        amount, cat, desc = t
        result.append(f"${amount:.2f} ({cat}) - {desc}")
    
    return "\n".join(result)

@mcp.tool()
async def add_category(name: str) -> str:
    """Add a new transaction category.
    
    Args:
        name: The name of the new category
    """
    if not name or len(name.strip()) == 0:
        return "Category name cannot be empty."
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return f"Category '{name}' added successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return f"Category '{name}' already exists."

@mcp.tool()
async def export_data(format: str = "json") -> str:
    """Export all transaction data.
    
    Args:
        format: Export format, currently only JSON is supported
    """
    if format.lower() != "json":
        return "Only JSON format is currently supported."
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions ORDER BY timestamp DESC")
    transactions = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    export_file = "transactions_export.json"
    with open(export_file, "w") as f:
        json.dump(transactions, f, indent=2)
    
    return f"Data exported to {export_file}"

if __name__ == "__main__":
    # Initialize the database
    initialize_db()
    
    # Initialize and run the server
    mcp.run(transport='stdio')