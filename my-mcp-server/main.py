from datetime import date
from fastmcp.server import FastMCP, Context
from typing import List
from mcp.types import SamplingMessage, TextContent
from portfolio_manager.portfolio import (
    get_portfolio_value,
    get_all_stocks,
    get_stock_position,
    add_stock,
    sell_stock,
    remove_stock
)

mcp = FastMCP("Portfolio Management Server", "1.0.0")


@mcp.tool()
def check_portfolio_value_tool() -> str:
    """Calculate the total value of the portfolio"""
    total_value = get_portfolio_value()

    return f"Total portfolio value: ${total_value:.2f}"


@mcp.tool()
def list_stocks_tool() -> str:
    """List all stocks in the portfolio with their details"""
    stocks = get_all_stocks()

    if not stocks:
        return "No stocks in the portfolio. Would you like to add some?"
    return "\n".join(stocks)


@mcp.tool()
def get_stock_position_tool(stock_symbol: str) -> str:
    """Get the current position(s) of a specific stock in the portfolio"""
    positions = get_stock_position(stock_symbol)

    if not positions:
        return f"Stock symbol '{stock_symbol.upper()}' not found in portfolio."
    return "\n".join(positions)


@mcp.tool()
async def get_stock_position_llm(stock_symbol: str, ctx: Context) -> List[SamplingMessage]:
    """
    Get the current position(s) of a specific stock in the portfolio,
    and ask the LLM on client side to summarize or explain the position.
    """
    positions = get_stock_position(stock_symbol)

    if not positions:
        user_message = f"Stock symbol '{stock_symbol.upper()}' not found in portfolio."
    else:
        user_message = "\n".join(positions)
    
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

    system_prompt = "You are a helpful financial assistant. Please summarize the stock position provided by the user in a concise and informative manner."
    return await ctx.sample(messages, system_prompt=system_prompt)


@mcp.tool()
def add_stock_tool(stock_symbol: str, shares: int, price_per_share: float, date_acquired: date) -> str:
    """Add a stock to the portfolio as a new position.
    if the date_acquired is not provided, it defaults to today."""
    return add_stock(stock_symbol, shares, price_per_share, date_acquired)


@mcp.tool()
def sell_stock_tool(stock_symbol: str, shares: int) -> str:
    """Sell a specified number of shares of a stock from the portfolio.
    Selling of the shares is using a FIFO (First In, First Out) method."""
    return sell_stock(stock_symbol, shares)


@mcp.tool()
def remove_stock_tool(stock_symbol: str) -> str:
    """Remove or Sell all positions of a stock from the portfolio"""
    return remove_stock(stock_symbol)


# Resource: Greeting
# As of June 2025, Claude Desktop does not support dynamic resources, so this will not show up yet it as your client.
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! How can I assist you with your portfolio today?"


if __name__ == "__main__":
    print("Hello from My MCP Server!")
    mcp.run(transport="stdio")