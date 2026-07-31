import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/server.py"],  # Path to your server entry point
        env=None
    )

    print("🔌 Connecting to EgyptAir MCP Server...")

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            # Step 2: Capability Handshake & Initialization
            print("\n🤝 Step 1: Performing Protocol Handshake...")
            
            # The client declares its capabilities here (e.g., enabling sampling)
            init_result = await session.initialize()
            
            print(f"✅ Handshake Complete!")
            print(f"   Server Name: {init_result.serverInfo.name}")
            print(f"   Server Version: {init_result.serverInfo.version}")
            print(f"   Server Capabilities: {list(init_result.capabilities.model_dump().keys())}")

            # Step 3: Discover Server Features
            print("\n🔍 Step 2: Discovering Available Tools, Resources & Prompts...")

            # 3a. Discover Tools
            tools_response = await session.list_tools()
            print(f"\n[Tools Found: {len(tools_response.tools)}]")
            for tool in tools_response.tools:
                print(f" - 🛠️  {tool.name}: {tool.description[:60]}...")

            # 3b. Discover Resources
            resources_response = await session.list_resources()
            print(f"\n[Resources Found: {len(resources_response.resources)}]")
            for res in resources_response.resources:
                print(f" - 📄 {res.name} ({res.uri})")

            # 3c. Discover Prompts
            prompts_response = await session.list_prompts()
            print(f"\n[Prompts Found: {len(prompts_response.prompts)}]")
            for prompt in prompts_response.prompts:
                print(f" - 💬 {prompt.name}")

            # Step 4: Test Operation - Read Resource (Policy Document)
            print("\n📖 Step 3: Reading a Resource (Delay Compensation Policy)...")
            try:
                # Target URI exposed by your resources handler
                policy_content = await session.read_resource("sql://policies")
                print("--- Resource Contents Received ---")
                print(policy_content.contents[0].text[:300] + "...\n")
            except Exception as e:
                print(f"⚠️ Could not read resource: {e}")

            # Step 5: Test Operation - Execute Tool (draft_passenger_email)
            print("🚀 Step 4: Calling Tool 'draft_passenger_email' (Triggers Sampling)...")
            try:
                # Testing with booking_id = 1
                result = await session.call_tool(
                    name="draft_passenger_email",
                    arguments={"booking_id": 1}
                )
                
                print("\n📩 Output from Server:")
                for content in result.content:
                    if content.type == "text":
                        print(content.text)
            except Exception as e:
                print(f"❌ Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(main())