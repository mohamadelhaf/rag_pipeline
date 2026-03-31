from fastmcp import FastMCP
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

mcp = FastMCP('hr_server')




EMPLOYEES = {
    "mohamad": {
        "name": "Mohamad Elhaf",
        "role": "Data & AI Engineer",
        "department": "DIGIT",
        "leave_balance": 25,
        "leave_taken": 3,
        "start_date": "2026-02-16",
        "manager": "Jean Dupont"
    },
    "jean": {
        "name": "Jean Dupont",
        "role": "Tech Lead",
        "department": "DIGIT",
        "leave_balance": 25,
        "leave_taken": 10,
        "start_date": "2023-01-10",
        "manager": "Marie Curie"
    }
}

@mcp.tool()
def get_employee_info(name:str) -> dict:
    name = name.lower().strip()

    if name not in EMPLOYEES:
        return {"error": "Employee not found."}
    return EMPLOYEES[name]

@mcp.tool()
def check_leave_balance(name:str) -> str:
    name = name.lower().strip()

    if name not in EMPLOYEES:
        return "Employee not found."
    
    emp = EMPLOYEES[name]
    remaining = emp["leave_balance"] - emp["leave_taken"]
    return (
        f"{emp['name']} has taken {emp['leave_taken']} days of leave."
        f"out of {emp['leave_balance']} days ."
        f"Remaining leave balance is {remaining} days."
        )

@mcp.tool()
def list_employees() -> list:
    return [emp['name'] for emp in EMPLOYEES.values()]

if __name__ =="__main__":
    mcp.run()


    

