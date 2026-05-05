from fastmcp import FastMCP
from datetime import datetime, timedelta
from dotenv import load_dotenv
import msal
import requests
import os


load_dotenv()

mcp = FastMCP('calendar_server')

SCOPES = ['https://graph.microsoft.com/Calendars.Read',
          'https://graph.microsoft.com/Calendars.ReadWrite']


def get_access_token():
    app = msal.PublicClientApplication(
        client_id=os.getenv("AZURE_CLIENT_ID"),
        authority=f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}"
    )

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # fix: was app.acquire.token.interactive (invalid attribute chain)
    result = app.acquire_token_interactive(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]

    # fix: was 'error description' (space is invalid key)
    raise Exception(f"Could not get token: {result.get('error_description')}")


def graph_get(endpoint: str) -> dict:
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers)
    response.raise_for_status()
    return response.json()


def graph_post(endpoint: str, data: dict) -> dict:
    token = get_access_token()
    # fix: was "Contetn-Type" (typo)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # fix: was `response = response.post(...)` — called before assignment
    response = requests.post(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers, json=data)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_events(date: str = "today") -> list:
    if date == "today":
        date = datetime.now().strftime("%Y-%m-%d")
    elif date == "tomorrow":
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    start = f"{date}T00:00:00"
    end = f"{date}T23:59:59"

    data = graph_get(
        f"/me/calendarView?startDateTime={start}&endDateTime={end}"
        f"&$select=subject,start,end,attendees,location"
        f"&$orderby=start/dateTime"
    )

    events = []
    for event in data.get("value", []):
        events.append({
            "title": event.get("subject", "No title"),
            # fix: was event("start", {}) — dict called as function
            "start": event.get("start", {}).get("dateTime"),
            "end": event.get("end", {}).get("dateTime"),
            # fix: was "locaton" (typo)
            "location": event.get("location", {}).get("displayName"),
            "attendees": [a.get("emailAddress", {}).get("name") for a in event.get("attendees", [])]
        })

    if not events:
        return [{"message": f"No events found for {date}"}]
    return events


@mcp.tool()
def get_upcoming_events(days: int = 7) -> list:
    start = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

    # fix: was two separate args to graph_get() due to trailing comma — must be one string
    data = graph_get(
        f"/me/calendarView?startDateTime={start}&endDateTime={end}"
        f"&$select=subject,start,end,attendees,location"
        f"&$orderby=start/dateTime"
    )

    events = []
    for event in data.get("value", []):
        events.append({
            "title": event.get("subject"),
            "start": event.get("start", {}).get("dateTime"),
            "end": event.get("end", {}).get("dateTime"),
            "location": event.get("location", {}).get("displayName"),
            "attendees": [a.get("emailAddress", {}).get("name") for a in event.get("attendees", [])]
        })

    if not events:
        return [{"message": f"No events in the next {days} days"}]
    return events


@mcp.tool()
# fix: was `location: str = []` — mutable default and wrong type
def create_event(title: str, date: str, start_time: str, end_time: str,
                 attendees: list, location: str = "") -> dict:
    event_data = {
        # fix: was "subejct" (typo)
        "subject": title,
        "start": {
            "dateTime": f"{date}T{start_time}",
            # fix: was "TimeZone" — MS Graph uses camelCase "timeZone"
            "timeZone": "Europe/Paris"
        },
        "end": {
            "dateTime": f"{date}T{end_time}",
            "timeZone": "Europe/Paris"
        },
        # fix: was "Type" — MS Graph uses lowercase "type"
        "attendees": [{"emailAddress": {"address": email}, "type": "required"} for email in attendees]
    }

    if location:
        event_data["location"] = {"displayName": location}

    result = graph_post("/me/events", event_data)
    return {
        "status": "created",
        "id": result.get("id"),
        "title": result.get("subject"),
        "start": result.get("start", {}).get("dateTime"),
        "end": result.get("end", {}).get("dateTime"),
    }


if __name__ == "__main__":
    mcp.run()
