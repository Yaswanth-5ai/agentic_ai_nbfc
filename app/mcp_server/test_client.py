import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Configure how the MCP client starts the server.
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "app.mcp_server.server"],
    )

    # Start the server and establish communication.
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            # Initialize the MCP connection.
            await session.initialize()

            # Discover tools exposed by the server.
            tools_response = await session.list_tools()

            print("\nAvailable MCP tools:")

            for tool in tools_response.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call the outstanding balance tool.
            result = await session.call_tool(
                "outstanding_balance",
                arguments={"customer_id": "C001"},
            )

            print("\nOutstanding balance tool result:")
            for content in result.content:
                if content.type == "text":
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())