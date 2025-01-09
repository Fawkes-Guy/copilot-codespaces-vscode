import requests

# Tastytrade API Base URL
BASE_URL = "https://api.tastytrade.com"

# Replace with your login details
USERNAME = "dayanapb27"
PASSWORD = "yjJ.@qcC.N7jByq2"

# Trade details: Manually input these for each trade
TRADE_DETAILS = {
    "contract_date": "2025-02-21",  # Option expiration date (YYYY-MM-DD)
    "contract_type": "Call",        # Call or Put
    "strike_1": 240,                # Strike price for the first leg
    "strike_2": 245,                # Strike price for the second leg
    "limit_price": 3.15,            # Your limit price for the trade
    "trade_type": "debit"           # 'debit' or 'credit' trade
}

def authenticate():
    """Authenticate with Tastytrade and return a session token."""
    session_url = f"{BASE_URL}/sessions"
    payload = {"login": USERNAME, "password": PASSWORD}
    
    response = requests.post(session_url, json=payload)
    if response.status_code == 201:
        token = response.json()["data"]["session-token"]
        print("Authentication Successful!")
        return token
    else:
        print(f"Authentication Failed: {response.status_code} - {response.text}")
        return None

def get_accounts(token):
    """Fetch account IDs linked to the authenticated user."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/accounts", headers=headers)
    
    if response.status_code == 200:
        accounts = response.json()["data"]
        account_ids = [account["account-number"] for account in accounts]
        print("Fetched Account IDs:", account_ids)
        return account_ids
    else:
        print(f"Failed to fetch accounts: {response.status_code} - {response.text}")
        return []

def place_order(token, account_id, trade_details, action="open"):
    """Place orders for a given account."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Determine order legs (BTO, STO for opening or BTC, STC for closing)
    if action == "open":
        leg1_action = "BTO"  # Buy To Open
        leg2_action = "STO"  # Sell To Open
    else:
        leg1_action = "BTC"  # Buy To Close
        leg2_action = "STC"  # Sell To Close
    
    order_payload = {
        "order-type": "Limit",
        "price": trade_details["limit_price"],
        "time-in-force": "Day",
        "legs": [
            {
                "instrument-type": "Equity Option",
                "action": leg1_action,
                "quantity": 1,
                "symbol": f"AAPL {trade_details['contract_date']} {trade_details['strike_1']} {trade_details['contract_type']}"
            },
            {
                "instrument-type": "Equity Option",
                "action": leg2_action,
                "quantity": 1,
                "symbol": f"AAPL {trade_details['contract_date']} {trade_details['strike_2']} {trade_details['contract_type']}"
            }
        ]
    }
    
    # Send order request
    response = requests.post(f"{BASE_URL}/accounts/{account_id}/orders", json=order_payload, headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        print(f"Order placed successfully for account {account_id}")
    else:
        print(f"Failed to place order for account {account_id}: {response.status_code} - {response.text}")

def main():
    # Step 1: Authenticate and get session token
    token = authenticate()
    if not token:
        return
    
    # Step 2: Fetch account IDs
    account_ids = get_accounts(token)
    if not account_ids:
        return
    
    # Step 3: Place orders for all accounts
    print("\nPlacing Orders (BTO & STO) for All Accounts...")
    for account_id in account_ids:
        place_order(token, account_id, TRADE_DETAILS, action="open")
    
    # Step 4: Ask user if they want to close trades
    close = input("\nDo you want to close these trades? (yes/no): ").strip().lower()
    if close == "yes":
        print("\nClosing Orders (BTC & STC) for All Accounts...")
        for account_id in account_ids:
            place_order(token, account_id, TRADE_DETAILS, action="close")
    else:
        print("Trades left open. Exiting...")

if __name__ == "__main__":
    main()
