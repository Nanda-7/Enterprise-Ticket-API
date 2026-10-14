import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
WEBHOOK_URL = "http://127.0.0.1:9000"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
API_KEY = os.getenv("API_KEY")

# Retry strategy for GET requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

session = requests.Session()
session.mount("http://", HTTPAdapter(max_retries=retry_strategy))

try:
    # 1. Get OAuth2 access token
    token_response = requests.post(
        f"{BASE_URL}/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        timeout=10
    )
    token_response.raise_for_status()

    access_token = token_response.json()["access_token"]
    print("Access token received!")

    # 2. Fetch tickets using OAuth2
    response = session.get(
        f"{BASE_URL}/oauth/tickets",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10
    )
    response.raise_for_status()

    tickets = response.json()
    print("Tickets fetched successfully:", tickets)

    # 3. Send tickets to webhook
    webhook_response = requests.post(
        WEBHOOK_URL,
        json=tickets,
        timeout=10
    )
    webhook_response.raise_for_status()
    print("Tickets sent to webhook successfully!")

    # 4. Save execution log
    with open("output.json", "w") as file:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "tickets_sent": len(tickets["tickets"])
        }, file, indent=4)

    print("Results saved to output.json")

except requests.exceptions.Timeout:
    print("Request timed out")

except requests.exceptions.HTTPError as error:
    print("HTTP error:", error)

except requests.exceptions.RequestException as error:
    print("Request failed:", error)

except (KeyError, ValueError) as error:
    print("Unexpected API response:", error)
