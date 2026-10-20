
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Connect to the MCP server and execute a tool."""

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "app.mcp_server.server"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            if result.isError:
                raise RuntimeError(f"MCP tool failed: {tool_name}")

            for content in result.content:
                if content.type == "text":
                    return json.loads(content.text)

            raise RuntimeError("MCP tool returned no text result.")


if __name__ == "__main__":
    async def main():
        result = await call_mcp_tool(
            "outstanding_balance",
            {"customer_id": "C001"},
        )
        print(json.dumps(result, indent=2))

    asyncio.run(main())