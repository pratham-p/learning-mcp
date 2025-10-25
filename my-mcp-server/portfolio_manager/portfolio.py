# Portfolio Management Functions
# This module provides functions to manage a stock portfolio, including adding, selling, and checking stocks.

from datetime import date
from typing import Dict, List, Optional


# The portfolio data structure
my_portfolio: Dict[str, List[dict]] = {
    "AAPL": [
        {"shares": 10, "price_per_share": 150.0, "date_acquired": "2025-01-15"},
        {"shares": 10, "price_per_share": 250.0, "date_acquired": "2025-10-15"}
    ],
    "GOOGL": [
        {"shares": 5, "price_per_share": 2800.0, "date_acquired": "2025-02-20"}
    ],
    "AMZN": [
        {"shares": 2, "price_per_share": 3400.0, "date_acquired": "2025-03-10"}
    ],
    "MSFT": [
        {"shares": 8, "price_per_share": 300.0, "date_acquired": "2025-04-05"}
    ],
    "TSLA": [
        {"shares": 3, "price_per_share": 700.0, "date_acquired": "2025-05-12"}
    ],
}


# Check total portfolio value
def get_portfolio_value() -> float:
    """Calculate the total value of the portfolio."""
    return sum(
        position["shares"] * position["price_per_share"]
        for stocks in my_portfolio.values()
        for position in stocks
    )


# Get all stocks in the portfolio with their details
def get_all_stocks() -> List[str]:
    """List all stocks in the portfolio with their details."""
    stock_list = []
    for stock_symbol, positions in my_portfolio.items():
        for idx, details in enumerate(positions, 1):
            stock_list.append(
                f"{stock_symbol} (Position {idx}): {details['shares']} shares at ${details['price_per_share']:.2f} per share, acquired on {details.get('date_acquired', 'unknown date')}."
            )
    return stock_list


# Get all positions of a specific stock in the portfolio
def get_stock_position(stock_symbol: str) -> Optional[List[str]]:
    """Get the current position(s) of a specific stock in the portfolio."""
    stock_symbol = stock_symbol.upper()
    if stock_symbol not in my_portfolio:
        return None
    positions = my_portfolio[stock_symbol]
    result = []
    for idx, position in enumerate(positions, 1):
        result.append(
            f"{stock_symbol} (Position {idx}): {position['shares']} shares at ${position['price_per_share']:.2f} per share, acquired on {position.get('date_acquired', 'unknown date')}."
        )
    return result


# Add a new stock to the portfolio as a new position or add to an existing position
def add_stock(stock_symbol: str, shares: int, price_per_share: float, date_acquired: date) -> str:
    """Add a stock to the portfolio as a new position."""
    if shares <= 0 or price_per_share <= 0:
        return "Shares and price per share must be greater than zero."
    if not stock_symbol.isalpha():
        return "Stock symbol must contain only alphabetic characters."
    if len(stock_symbol) < 1 or len(stock_symbol) > 5:
        return "Stock symbol must be between 1 and 5 characters long."
    
    stock_symbol = stock_symbol.upper()
    position = {"shares": shares, "price_per_share": price_per_share, "date_acquired": date_acquired.isoformat()}

    if stock_symbol in my_portfolio:
        my_portfolio[stock_symbol].append(position)
    else:
        my_portfolio[stock_symbol] = [position]

    return f"Added {shares} shares of {stock_symbol} at ${price_per_share:.2f} per share as a new position."


# Sell a specified number of shares of a stock from the portfolio (FIFO)
def sell_stock(stock_symbol: str, shares: int) -> str:
    """Sell a specified number of shares of a stock from the portfolio (FIFO)."""
    stock_symbol = stock_symbol.upper()
    if stock_symbol not in my_portfolio:
        return f"Stock '{stock_symbol}' not found in portfolio."
    
    positions = my_portfolio[stock_symbol]
    total_shares = sum(position["shares"] for position in positions)
    
    if shares <= 0:
        return "Shares to sell must be greater than zero."
    
    if shares > total_shares:
        return f"Cannot sell {shares} shares of {stock_symbol}. Only {total_shares} shares available"
    
    # FIFO sell
    remaining_shares = shares
    positions.sort(key=lambda x: x["date_acquired"])
    idx = 0
    while remaining_shares > 0 and idx < len(positions):
        position = positions[idx]
        if position["shares"] <= remaining_shares:
            remaining_shares -= position["shares"]
            positions.pop(idx)
        else:
            position["shares"] -= remaining_shares
            remaining_shares = 0
            idx += 1
    
    if not positions:
        del my_portfolio[stock_symbol]
        return f"Sold all shares of {stock_symbol}. No remaining positions."
    
    return f"Sold {shares} shares of {stock_symbol}. Remaining shares: {sum(position['shares'] for position in positions)}."


# Remove or Sell all positions of a stock from the portfolio
def remove_stock(stock_symbol: str) -> str:
    """Remove or Sell all positions of a stock from the portfolio."""
    stock_symbol = stock_symbol.upper()
    
    if stock_symbol not in my_portfolio:
        return f"Stock '{stock_symbol}' not found in portfolio."
    
    del my_portfolio[stock_symbol]
    
    return f"Removed all positions of {stock_symbol} from the portfolio."