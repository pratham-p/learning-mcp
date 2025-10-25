import asyncio
import os
from dotenv import load_dotenv, find_dotenv
import openai
from fastmcp import Client
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext

# Find and load environment variables
env_path = find_dotenv()
if not env_path:
    raise ValueError("Could not find .env file!")
print(f"Found .env file at: {env_path}")

# Load environment variables
if not load_dotenv(env_path):
    raise ValueError("Failed to load .env file!")

# Check and set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file!")
print(f"Found OpenAI API Key (starts with): {api_key[:4]}...")

# Set the API key for the openai module
openai.api_key = api_key

# Verify OpenAI configuration
print(f"OpenAI API Key verification:")
print(f"- Key in environment: {'Yes' if api_key else 'No'}")
print(f"- Key in openai module: {'Yes' if openai.api_key else 'No'}")
if openai.api_key:
    print(f"- Key starts with: {openai.api_key[:4]}")

async def sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    ctx: RequestContext,
) -> str:
    print("\n=== Starting LLM Analysis ===")
    print(f"Number of messages received: {len(messages)}")
    
    # Convert MCP messages to OpenAI chat format
    chat_messages = []
    
    # Process each message
    for msg in messages:
        try:
            text_content = msg.content.text
            role = msg.role if msg.role in ["system", "user", "assistant"] else "user"
            chat_messages.append({
                "role": role,
                "content": text_content
            })
            print(f"\nAdded message - Role: {role}")
            print(f"Content: {text_content}")
        except Exception as e:
            print(f"Error processing message: {e}")
            continue
    
    if not chat_messages:
        print("No valid messages to process!")
        return "Error: No valid messages to analyze"
    
    print("\nPreparing GPT-4 request with the following messages:")
    for msg in chat_messages:
        print(f"- {msg['role']}: {msg['content'][:1000]}...")
    
    try:
        print("\nSending request to GPT-4...")
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=chat_messages,
            max_tokens=500,
            temperature=0.7,
        )

        # Normalize the returned content to a string. Some OpenAI client
        # variants return a dict like {'type': 'text', 'text': '...'} as the
        # message content; fastmcp expects a plain string. Handle several
        # possible shapes and fall back to str(response) as a last resort.
        try:
            choice = response.choices[0]
        except Exception:
            choice = None

        message_obj = None
        if isinstance(choice, dict):
            # choices can be dicts depending on client
            message_obj = choice.get("message") or choice.get("delta") or choice.get("text")
        else:
            message_obj = getattr(choice, "message", None)

        content = None
        if isinstance(message_obj, dict):
            # message object might contain 'content' or 'text'
            content = message_obj.get("content") or message_obj.get("text") or message_obj.get("delta")
        else:
            # message_obj might be an object with attribute 'content'
            content = getattr(message_obj, "content", None) if message_obj is not None else None

        # If content itself is a dict (e.g., {'type': 'text', 'text': '...'}), extract text
        if isinstance(content, dict):
            content_text = content.get("text") or content.get("content") or str(content)
        else:
            content_text = content

        # Final fallback
        if content_text is None:
            # Try other known positions
            try:
                # Some SDKs expose message as choice.message.content
                content_text = getattr(response.choices[0].message, "content", None)
            except Exception:
                content_text = None

        if content_text is None:
            # Last resort: stringify the full response
            content_text = str(response)

        llm_response = str(content_text)

        print("\n=== LLM Analysis Result ===")
        print(llm_response)
        print("\n=== Analysis Complete ===\n")
        return llm_response
        
    except Exception as e:
        print(f"\nError during LLM processing: {str(e)}")
        print(f"OpenAI API Key status: {'Set' if openai.api_key else 'Not Set'}")
        if openai.api_key:
            print(f"API Key starts with: {openai.api_key[:4]}...")
        raise

async def main():
    print("\nStarting Portfolio Analysis...")
    
    async with Client("./my-mcp-server/main.py", sampling_handler=sampling_handler) as client:
        try:
            print("\nCalling get_stock_position_llm tool...")
            response = await client.call_tool("get_stock_position_llm", {"stock_symbol": "AAPL"})
            
            print("\nTool Response:")
            print(f"Type: {type(response)}")
            print(f"Content: {response}")
            
            print("\nIf you don't see an LLM analysis above, the sampling handler wasn't triggered.")
            print("Sampling handler should be triggered automatically when receiving SamplingMessage objects.")
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise
        
if __name__ == "__main__":
    asyncio.run(main())
