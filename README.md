# Financial Tracker MCP Server

A Model Context Protocol (MCP) server that helps track financial transactions, manage budgets, and monitor spending patterns.

## Features

- Add income and expense transactions with categories
- View current balance and spending breakdown by category
- List and filter transactions by category

## Available Categories

- Income
- Food
- Transportation
- Utilities
- Entertainment
- Other

## Usage Examples

1. Add a new expense:
   - "Add a $50 expense for dinner under Food category"
   - "Record $1000 income from salary"

2. Check balance:
   - "What's my current balance?"
   - "Show me spending by category"

3. View transactions:
   - "Show all my transactions"
   - "List all Food expenses"

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python financial_tracker.py
```

The server uses in-memory storage for demonstration purposes. In a production environment, you should implement proper database storage.