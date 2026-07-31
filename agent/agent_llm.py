import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import mcp.types as mcp_types

import copy
load_dotenv()




MODEL_ID = "gemini-3.1-flash-lite"  

def clean_schema(schema_dict: dict) -> dict:
    """Removes fields incompatible with Gemini API function declarations."""
    if not isinstance(schema_dict, dict):
        return schema_dict

    cleaned = copy.deepcopy(schema_dict)
    
    # Remove top-level or nested keys that Gemini SDK rejects
    cleaned.pop("additionalProperties", None)
    cleaned.pop("additional_properties", None)
    cleaned.pop("$schema", None)

    # Clean properties recursively
    if "properties" in cleaned and isinstance(cleaned["properties"], dict):
        for prop_name, prop_val in cleaned["properties"].items():
            if isinstance(prop_val, dict):
                cleaned["properties"][prop_name] = clean_schema(prop_val)

    return cleaned
class MCPGeminiClient:
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def sampling_handler(self, context, request: mcp_types.CreateMessageRequestParams):
        """
        Sampling Handler: Serves as the callback when the MCP server requests 
        a text generation sample via `ctx.session.create_message`.
        """
        print("\n📬 [SAMPLING REQUEST RECEIVED FROM MCP SERVER]")
        
        # Extract prompt text sent by the MCP Server
        prompt_text = ""
        for msg in request.messages:
            if hasattr(msg.content, "text"):
                prompt_text += msg.content.text + "\n"
            elif isinstance(msg.content, dict) and msg.content.get("type") == "text":
                prompt_text += msg.content.get("text", "") + "\n"

        system_instruction = request.systemPrompt or "You are an AI assistant helping an MCP server generate communications."

        print(f"   Generating response using Gemini ({MODEL_ID})...")

        # Use Gemini to fulfill the server's sampling request
        response = await self.genai_client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=request.maxTokens or 350
            )
        )

        generated_text = response.text or ""
        print("✅ [SAMPLING COMPLETED & SENT BACK TO SERVER]")

        # Return structured sampling message back to the MCP Server
        return mcp_types.CreateMessageResult(
            role="assistant",
            content=mcp_types.TextContent(
                type="text",
                text=generated_text
            ),
            model=MODEL_ID
        )

    async def run(self):
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
            env=None
        )

        print(f"🔌 Connecting to MCP Server at '{self.server_script_path}'...")

        async with stdio_client(server_params) as (read_stream, write_stream):
            # Pass sampling_callback during ClientSession initialization
            async with ClientSession(
                read_stream, 
                write_stream, 
                sampling_callback=self.sampling_handler
            ) as session:
                
                # -------------------------------------------------------------
                # 1. Capability Handshake
                # -------------------------------------------------------------
                print("\n🤝 Handshake & Initializing Capabilities...")
                init_result = await session.initialize()
                print(f"✅ Connected to: {init_result.serverInfo.name} v{init_result.serverInfo.version}")

                # -------------------------------------------------------------
                # 2. Tool Discovery & Function Declaration Conversion
                # -------------------------------------------------------------
                mcp_tools = await session.list_tools()
                print(f"\n🛠️ Discovered {len(mcp_tools.tools)} MCP Tools:")
                
                function_declarations = []

                for tool in mcp_tools.tools:
                    print(f" - {tool.name}: {tool.description[:60]}...")
                    cleaned_params = clean_schema(tool.inputSchema)
                    function_declarations.append({
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": cleaned_params
                    })

                # Wrap tools into Google GenAI Tool declaration
                gemini_tools = [types.Tool(function_declarations=function_declarations)] if function_declarations else []

                # -------------------------------------------------------------
                # 3. Interactive Gemini Agent Loop
                # -------------------------------------------------------------
                print("\n✨ Gemini MCP Client Ready! Type 'exit' or 'quit' to quit.")
                
                # Maintain chat history
                chat_history = []

                while True:
                    user_input = input("\nUser > ").strip()
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    if not user_input:
                        continue

                    chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))

                    # Call Gemini with user input and available MCP tools
                    response = await self.genai_client.aio.models.generate_content(
                        model=MODEL_ID,
                        contents=chat_history,
                        config=types.GenerateContentConfig(
                            tools=gemini_tools
                        )
                    )

                    # Check if Gemini wants to call an MCP Tool
                    if response.function_calls:
                        for function_call in response.function_calls:
                            tool_name = function_call.name
                            tool_args = dict(function_call.args)

                            print(f"\n🤖 Gemini requested MCP tool: '{tool_name}' with args: {tool_args}")
                            
                            # Execute tool call on MCP Server
                            tool_result = await session.call_tool(
                                name=tool_name,
                                arguments=tool_args
                            )

                            # Format tool output back to Gemini
                            tool_output_text = "\n".join([c.text for c in tool_result.content if c.type == "text"])
                            print(f"⚙️ Tool Execution Output:\n{tool_output_text}")

                            # Add model function call and tool response to conversation history
                            chat_history.append(response.candidates[0].content)
                            chat_history.append(
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part.from_function_response(
                                            name=tool_name,
                                            response={"result": tool_output_text}
                                        )
                                    ]
                                )
                            )

                            # Request final answer from Gemini with tool response attached
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
    # Point this to your server entry point
    client = MCPGeminiClient(server_script_path="mcp_server/server.py")
    asyncio.run(client.run())