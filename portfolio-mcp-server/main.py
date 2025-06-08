from datetime import date
from fastmcp.server import FastMCP, Context
from typing import List
from mcp.types import SamplingMessage, TextContent

# mock data to simulate my stock positions in my portfolio
my_portfolio = {
    "AAPL": [
        {"shares": 10, "price_per_share": 150.0, "date_acquired": "2025-01-15"}
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

# Create MCP server
mcp = FastMCP("Portfolio Management Server", "1.0.0")

# Tool: Check portfolio value
@mcp.tool()
def check_portfolio_value() -> str:
    """Calculate the total value of the portfolio"""
    total_value = sum(
        position["shares"] * position["price_per_share"]
        for stocks in my_portfolio.values()
        for position in stocks
    )
    return f"Total portfolio value: ${total_value:.2f}"

# Tool: List all stocks in portfolio
@mcp.tool()
def list_stocks() -> str:
    """List all stocks in the portfolio with their details"""
    if not my_portfolio:
        return "No stocks in the portfolio. Would you like to add some?"
    
    stock_list = []
    for stock_symbol, positions in my_portfolio.items():
        for idx, details in enumerate(positions, 1):
            stock_list.append(
                f"{stock_symbol} (Position {idx}): {details['shares']} shares at ${details['price_per_share']:.2f} per share, acquired on {details.get('date_acquired', 'unknown date')}."
            )
    return "\n".join(stock_list)

# Tool: Get stock position
@mcp.tool()
def get_stock_position(stock_symbol: str) -> str:
    """Get the current position(s) of a specific stock in the portfolio"""
    stock_symbol = stock_symbol.upper()
    if stock_symbol not in my_portfolio:
        return f"Stock symbol '{stock_symbol}' not found in portfolio."
    
    positions = my_portfolio[stock_symbol]
    result = []
    for idx, position in enumerate(positions, 1):
        result.append(
            f"{stock_symbol} (Position {idx}): {position['shares']} shares at ${position['price_per_share']:.2f} per share, acquired on {position.get('date_acquired', 'unknown date')}."
        )
    return "\n".join(result)

@mcp.tool()
async def get_stock_position_llm(stock_symbol: str, ctx: Context) -> List[SamplingMessage]:
    """
    Get the current position(s) of a specific stock in the portfolio,
    but ask the LLM to summarize or explain the position.
    """
    stock_symbol = stock_symbol.upper()
    if stock_symbol not in my_portfolio:
        user_message = f"Stock symbol '{stock_symbol}' not found in portfolio."
    else:
        positions = my_portfolio[stock_symbol]
        details = []
        for idx, position in enumerate(positions, 1):
            details.append(
                f"{stock_symbol} (Position {idx}): {position['shares']} shares at ${position['price_per_share']:.2f} per share, acquired on {position.get('date_acquired', 'unknown date')}."
            )
        user_message = "\n".join(details)
    
    # Build list of SamplingMessages to return
    messages = [
        SamplingMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Details of stock position:\n{user_message}"
            )
        )
    ]
    
    # define systemPrompt params
    system_prompt = "You are a helpful financial assistant. Please summarize the stock position provided by the user in a concise and informative manner."
    return await ctx.sample(messages, system_prompt=system_prompt)

# Tool: Add stock to portfolio
@mcp.tool()
def add_stock(stock_symbol: str, shares: int, price_per_share: float, date_acquired: date) -> str:
    """Add a stock to the portfolio as a new position.
    if the date_acquired is not provided, it defaults to today."""
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

# Tool: Sell stock from portfolio
@mcp.tool()
def sell_stock(stock_symbol: str, shares: int) -> str:
    """Sell a specified number of shares of a stock from the portfolio.
    Selling of the shares is using a FIFO (First In, First Out) method."""
    stock_symbol = stock_symbol.upper()
    if stock_symbol not in my_portfolio:
        return f"Stock '{stock_symbol}' not found in portfolio."
    
    positions = my_portfolio[stock_symbol]
    total_shares = sum(position["shares"] for position in positions)
    
    if shares <= 0:
        return "Shares to sell must be greater than zero."
    if shares > total_shares:
        return f"Cannot sell {shares} shares of {stock_symbol}. Only {total_shares} shares available."
    
    # Sell shares
    remaining_shares = shares
    for position in positions.sort(key=lambda x: x["date_acquired"]):
        if remaining_shares <= 0:
            break
        if position["shares"] <= remaining_shares:
            remaining_shares -= position["shares"]
            positions.remove(position)
        else:
            position["shares"] -= remaining_shares
            remaining_shares = 0
    
    if not positions:
        del my_portfolio[stock_symbol]
        return f"Sold all shares of {stock_symbol}. No remaining positions."
    
    return f"Sold {shares} shares of {stock_symbol}. Remaining shares: {sum(position['shares'] for position in positions)}."

# Tool: Remove stock from portfolio
@mcp.tool()
def remove_stock(stock_symbol: str) -> str:
    """Remove or Sell all positions of a stock from the portfolio"""
    stock_symbol = stock_symbol.upper()
    if stock_symbol not in my_portfolio:
        return f"Stock '{stock_symbol}' not found in portfolio."
    
    del my_portfolio[stock_symbol]
    return f"Removed all positions of {stock_symbol} from the portfolio."

# Resource: Greeting
# As of June 2025, Claude Desktop does not support dynamic resources, so this will not show up yet it as your client.
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with your portfolio today?"

if __name__ == "__main__":
    print("Hello from My Portfolio MCP Server!")
    mcp.run(transport="stdio")