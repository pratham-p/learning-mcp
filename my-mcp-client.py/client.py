import asyncio
from dotenv import load_dotenv, find_dotenv
import openai
from fastmcp import Client
from fastmcp.client.sampling import SamplingMessage, SamplingParams, RequestContext

# Load environment variables
load_dotenv(find_dotenv())


async def sampling_handler(
    messages: list[SamplingMessage],
    params: SamplingParams,
    ctx: RequestContext,
) -> str:
    prompt = "\n".join([m.content.text for m in messages if m.content.type == "text"])
    print("Received prompt for LLM sampling:", prompt)
    system_prompt = params.systemPrompt or "You are a helpful assistant."
    print("Using system prompt:", system_prompt)

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message["content"]

async def main():
    
    async with Client("./portfolio-mcp-server/main.py", sampling_handler=sampling_handler) as client:
        # Example: Call a tool that triggers LLM sampling
        result = await client.call_tool("get_stock_position_llm", {"stock_symbol": "AAPL"})
        
        if len(result) > 0:
            for message in result:
                if message.type == "text":
                    print("LLM Response:", message.text)
        
        
if __name__ == "__main__":
    asyncio.run(main())
