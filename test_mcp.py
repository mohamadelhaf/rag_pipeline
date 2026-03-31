import asyncio
from fastmcp import Client

async def test_hr_server():
    print("Testing HR Server")
    async with Client("mcp_servers/hr_server.py") as client:
        result = await client.call_tool("list_employees", [])
        print("Employees:", result)

        result = await client.call_tool("get_employee_info", {"name":"mohamad"})
        print("Employee Info:", result)

        result = await client.call_tool("check_leave_balance", {"name":"mohamad"})
        print("Leave Balance:", result)

async def test_documents():
    print("Testing Documents Server")
    async with Client("mcp_servers/documents_server.py") as doc_client:
        result = await doc_client.call_tool("search_documents", {"query": "How many leave days", "agent": "hr"})
        print("Search Result:", result)

async def main():
    await test_hr_server()
    await test_documents()

if __name__ == "__main__":
    asyncio.run(main())


