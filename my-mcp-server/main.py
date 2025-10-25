from datetime import date
from fastmcp.server.server import FastMCP
from fastmcp.server.context import Context
from typing import List, Optional
from mcp.types import SamplingMessage, TextContent
import requests
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
async def get_stock_position_llm(stock_symbol: str, ctx: Context) -> str:
    """
    Get the current position(s) of a specific stock in the portfolio,
    and ask the LLM on client side to summarize or explain the position.
    Args:
        stock_symbol: The stock symbol to look up
        ctx: The request context for sampling
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

    system_prompt = "You are a helpful financial assistant. Please summarize the stock position provided by the user in a concise and informative manner. Include 1. Total number of shares\n2. Average purchase price\n3. Total investment value\n4. Acquisition date(s)\n5. Any relevant insights or recommendations based on the position details."
    # ctx.sample may return a rich TextContent object (or a dict) depending
    # on the MCP client implementation. The tool is declared to return a
    # plain string, so extract the textual content here to satisfy FastMCP's
    # output validation.
    sampled = await ctx.sample(messages, system_prompt=system_prompt)

    # If it's the TextContent dataclass or similar object, try to access `.text`
    try:
        text_val = getattr(sampled, "text", None)
    except Exception:
        text_val = None

    if text_val is None:
        # If it's a dict-like structure, pull the 'text' key
        try:
            if isinstance(sampled, dict):
                text_val = sampled.get("text") or sampled.get("content")
        except Exception:
            text_val = None

    # Fallback to stringifying the sampled value
    if text_val is None:
        text_val = str(sampled)

    return text_val


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


@mcp.tool()
def web_search_tool(query: str, num_results: Optional[int] = 5) -> str:
    """
    Perform a web search and return the results.
    
    Args:
        query: The search query string
        num_results: Number of results to return (default: 5)
    """
    base_url = "https://api.duckduckgo.com/"
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        # Add the abstract if available
        if data.get('Abstract'):
            results.append(f"Summary: {data['Abstract']}")
            
        # Add related topics
        for topic in data.get('RelatedTopics', [])[:num_results]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append(f"- {topic['Text']}")
                
        if not results:
            return "No results found for your query."
            
        return "\n".join(results)
        
    except Exception as e:
        return f"Error performing web search: {str(e)}"


if __name__ == "__main__":
    print("Hello from My MCP Server!")
    mcp.run(transport="stdio")