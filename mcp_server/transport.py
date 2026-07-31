import asyncio
import os
import copy
from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import ClientSession
from mcp.client.sse import sse_client  # <-- Use SSE client import
import mcp.types as mcp_types

load_dotenv()
MODEL_ID ="gemini-3.1-flash-lite"  

def clean_schema(schema_dict: dict) -> dict:
    if not isinstance(schema_dict, dict):
        return schema_dict
    cleaned = copy.deepcopy(schema_dict)
    cleaned.pop("additionalProperties", None)
    cleaned.pop("additional_properties", None)
    cleaned.pop("$schema", None)
    if "properties" in cleaned and isinstance(cleaned["properties"], dict):
        for prop_name, prop_val in cleaned["properties"].items():
            if isinstance(prop_val, dict):
                cleaned["properties"][prop_name] = clean_schema(prop_val)
    return cleaned

class MCPGeminiClient:
    def __init__(self, server_url: str = "http://localhost:8000/sse"):
        self.server_url = server_url
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def sampling_handler(self, context, request: mcp_types.CreateMessageRequestParams):
        print("\n📬 [SAMPLING REQUEST RECEIVED OVER HTTP]")
        prompt_text = ""
        for msg in request.messages:
            if hasattr(msg.content, "text"):
                prompt_text += msg.content.text + "\n"
            elif isinstance(msg.content, dict) and msg.content.get("type") == "text":
                prompt_text += msg.content.get("text", "") + "\n"

        system_instruction = request.systemPrompt or "You are an AI assistant."
        
        response = await self.genai_client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=request.maxTokens or 350
            )
        )

        return mcp_types.CreateMessageResult(
            role="assistant",
            content=mcp_types.TextContent(type="text", text=response.text or ""),
            model=MODEL_ID
        )

    async def run(self):
        print(f"🔌 Connecting to EgyptAir MCP SSE Endpoint at '{self.server_url}'...")

        # Connect over SSE stream instead of stdio
        async with sse_client(self.server_url) as (read_stream, write_stream):
            async with ClientSession(
                read_stream, 
                write_stream, 
                sampling_callback=self.sampling_handler
            ) as session:
                
                print("\n🤝 Handshake & Initializing Capabilities over HTTP...")
                init_result = await session.initialize()
                print(f"✅ Connected to: {init_result.serverInfo.name}")

                # Discover Tools
                mcp_tools = await session.list_tools()
                function_declarations = []
                for tool in mcp_tools.tools:
                    print(f" - {tool.name}: {tool.description[:60]}...")
                    function_declarations.append({
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": clean_schema(tool.inputSchema)
                    })

                gemini_tools = [types.Tool(function_declarations=function_declarations)] if function_declarations else []

                print("\n✨ Gemini MCP Client Ready (HTTP SSE Mode)! Type 'exit' to quit.")
                chat_history = []

                while True:
                    user_input = input("\nUser > ").strip()
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    if not user_input:
                        continue

                    chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))

                    response = await self.genai_client.aio.models.generate_content(
                        model=MODEL_ID,
                        contents=chat_history,
                        config=types.GenerateContentConfig(tools=gemini_tools)
                    )

                    if response.function_calls:
                        for function_call in response.function_calls:
                            tool_name = function_call.name
                            tool_args = dict(function_call.args)

                            print(f"\n🤖 Calling MCP tool over HTTP: '{tool_name}'")
                            tool_result = await session.call_tool(name=tool_name, arguments=tool_args)

                            tool_output_text = "\n".join([c.text for c in tool_result.content if c.type == "text"])
                            
                            chat_history.append(response.candidates[0].content)
                            chat_history.append(
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_function_response(name=tool_name, response={"result": tool_output_text})]
                                )
                            )

                            final_response = await self.genai_client.aio.models.generate_content(
                                model=MODEL_ID,
                                contents=chat_history,
                                config=types.GenerateContentConfig(tools=gemini_tools)
                            )
                            print(f"\nGemini > {final_response.text}")
                            chat_history.append(final_response.candidates[0].content)

                    else:
                        print(f"\nGemini > {response.text}")
                        chat_history.append(response.candidates[0].content)

if __name__ == "__main__":
    client = MCPGeminiClient("http://localhost:8000/sse")
    asyncio.run(client.run())