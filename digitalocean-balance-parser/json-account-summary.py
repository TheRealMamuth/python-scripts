import json
import os
import requests
import argparse

EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/USD"

def get_usd_to_pln_rate():
    """
    Fetch the current exchange rate for USD to PLN.
    """
    response = requests.get(EXCHANGE_API_URL)
    if response.status_code == 200:
        data = response.json()
        return data["rates"]["PLN"]
    else:
        print(f"Failed to fetch exchange rate. Error: {response.status_code} - {response.text}")
        return None

def send_to_discord(webhook_url, message):
    # ... [rest of the function remains unchanged]

def save_to_file(filename, message):
    # ... [rest of the function remains unchanged]

def main():
    # ... [beginning of the function remains unchanged]

    usd_to_pln_rate = get_usd_to_pln_rate()
    if not usd_to_pln_rate:
        print("Failed to retrieve exchange rate. Exiting.")
        return

    total_month_to_date_balance_pln = total_month_to_date_balance * usd_to_pln_rate

    message = f"""
📊 **---===### SUMMARY ###===---**
💵 Month to Date Balance (USD): {total_month_to_date_balance:.2f} USD
💰 Month to Date Balance (PLN): {total_month_to_date_balance_pln:.2f} PLN
🔒 Account Balance (USD): {total_account_balance:.2f} USD
📈 Month to Date Usage (USD): {total_month_to_date_usage:.2f} USD
"""

    # ... [rest of the function remains unchanged]

if __name__ == "__main__":
    main()
